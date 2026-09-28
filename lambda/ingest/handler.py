import json
import base64
import uuid
import logging
from shared.config import config
from shared.aws_clients import get_s3_client, get_sqs_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = get_s3_client()
sqs = get_sqs_client()


def lambda_handler(event, context):
    path = event.get("path", "")
    logger.info(f"Path: {path}")
    
    try:
        if path == "/ask":
            return handle_text(event)
        elif path == "/ask-audio":
            return handle_audio(event)
        else:
            return response(400, {"error": f"Unknown path: {path}"})
    except Exception as e:
        logger.exception("Ingest failed")
        return response(500, {"error": str(e)})


def handle_text(event):
    body = json.loads(event.get("body") or "{}")
    text = body.get("text", "").strip()
    
    if not text:
        return response(400, {"error": "text is required"})
    
    request_id = str(uuid.uuid4())
    
    message = {
        "request_id": request_id,
        "input_type": "text",
        "text": text,
        "voice": body.get("voice", "ru_RU-irina-medium"),
        "speed": float(body.get("speed", 1.0)),
        "volume": float(body.get("volume", 1.0)),
        "pitch": float(body.get("pitch", 1.0)),
        "format": body.get("format", "mp3"),
    }
    
    sqs.send_message(
        QueueUrl=config.SQS_INPUT_URL,
        MessageBody=json.dumps(message, ensure_ascii=False),
    )
    
    logger.info(f"Text queued: request_id={request_id}")
    return response(200, {"request_id": request_id})


def handle_audio(event):
    body = json.loads(event.get("body") or "{}")
    audio_b64 = body.get("audio")
    
    if not audio_b64:
        return response(400, {"error": "audio is required"})
    
    request_id = str(uuid.uuid4())
    audio_bytes = base64.b64decode(audio_b64)
    s3_key = f"{request_id}.wav"
    
    s3.put_object(
        Bucket=config.S3_AUDIO_INPUT,
        Key=s3_key,
        Body=audio_bytes,
        ContentType="audio/wav",
    )
    
    message = {
        "request_id": request_id,
        "input_type": "audio",
        "s3_uri": f"s3://{config.S3_AUDIO_INPUT}/{s3_key}",
        "voice": body.get("voice", "ru_RU-irina-medium"),
        "speed": float(body.get("speed", 1.0)),
        "volume": float(body.get("volume", 1.0)),
        "pitch": float(body.get("pitch", 1.0)),
        "format": body.get("format", "mp3"),
    }
    
    sqs.send_message(
        QueueUrl=config.SQS_INPUT_URL,
        MessageBody=json.dumps(message, ensure_ascii=False),
    )
    
    logger.info(f"Audio queued: request_id={request_id}, key={s3_key}")
    return response(200, {"request_id": request_id})


def response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, ensure_ascii=False),
    }