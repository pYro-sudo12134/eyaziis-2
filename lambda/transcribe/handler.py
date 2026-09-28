import json
import logging
from urllib.parse import urlparse

from shared.aws_clients import get_s3_client, get_transcribe_client
from shared.config import config
from shared.requests_db import mark_failed

logger = logging.getLogger()
logger.setLevel(logging.INFO)

transcribe = get_transcribe_client()
s3 = get_s3_client()


def lambda_handler(event, context):
    action = event.get("action")
    logger.info(f"Transcribe action: {action}")

    if action == "start":
        return start_transcription(event)
    elif action == "check":
        return check_transcription(event)
    elif action == "parse":
        return parse_transcript(event)
    elif action == "mark_failed":
        mark_failed(event["request_id"], event.get("error", "unknown"))
        return {"status": "ok"}
    else:
        raise ValueError(f"Unknown action: {action}")


def start_transcription(event):
    s3_uri = event["s3_uri"]
    request_id = event["request_id"]
    job_name = f"job-{request_id}"

    logger.info(f"Starting transcription: {job_name}, uri={s3_uri}")

    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": s3_uri},
        MediaFormat="wav",
        LanguageCode=config.TRANSCRIBE_LANGUAGE,
        OutputBucketName=config.S3_TRANSCRIPTS,
    )

    return {
        "job_name": job_name,
        "request_id": request_id,
        "status": "IN_PROGRESS",
        "attempts": 0,
    }


def check_transcription(event):
    job_name = event["job_name"]
    request_id = event.get("request_id", "")
    attempts = event.get("attempts", 0) + 1

    response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    status = response["TranscriptionJob"]["TranscriptionJobStatus"]

    logger.info(f"Job {job_name}: status={status}, attempts={attempts}")

    result = {
        "job_name": job_name,
        "request_id": request_id,
        "status": status,
        "attempts": attempts,
        "transcript_uri": None,
        "error": None,
    }

    if status == "COMPLETED":
        result["transcript_uri"] = response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
    elif status == "FAILED":
        mark_failed(request_id, "Transcription job failed")
        result["error"] = "Transcription failed"

    return result


def parse_transcript(event):
    job_name = event["job_name"]
    request_id = event.get("request_id", "")

    response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    transcript_uri = response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]

    bucket, key = parse_s3_uri(transcript_uri)

    obj = s3.get_object(Bucket=bucket, Key=key)
    data = json.loads(obj["Body"].read())

    text = data["results"]["transcripts"][0]["transcript"]
    logger.info(f"Parsed transcript: {text[:100]}...")

    return {
        "text": text,
        "request_id": request_id,
    }


def parse_s3_uri(uri: str) -> tuple[str, str]:
    if uri.startswith("s3://"):
        parsed = urlparse(uri)
        return parsed.netloc, parsed.path.lstrip("/")

    parsed = urlparse(uri)
    parts = parsed.path.lstrip("/").split("/", 1)
    return parts[0], parts[1]
