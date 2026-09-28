import json
import logging

from shared.aws_clients import get_s3_client
from shared.config import config
from shared.requests_db import get_request

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = get_s3_client()


def lambda_handler(event, context):
    path_params = event.get("pathParameters") or {}
    request_id = path_params.get("request_id")

    if not request_id:
        return response(400, {"error": "request_id is required"})

    item = get_request(request_id)

    if not item:
        return response(404, {"error": "request not found"})

    status = item.get("status", {}).get("S", "UNKNOWN")

    if status == "IN_PROGRESS":
        return response(
            200,
            {
                "request_id": request_id,
                "status": "IN_PROGRESS",
            },
        )

    if status == "FAILED":
        return response(
            200,
            {
                "request_id": request_id,
                "status": "FAILED",
                "error": item.get("error", {}).get("S", "unknown error"),
            },
        )

    s3_key = item["s3_key"]["S"]
    fmt = item.get("format", {}).get("S", "mp3")
    text = item.get("text", {}).get("S", "")

    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": config.S3_AUDIO_OUTPUT, "Key": s3_key},
        ExpiresIn=3600,
    )

    if config.AWS_ENDPOINT_URL != config.AWS_EXTERNAL_ENDPOINT:
        url = url.replace(config.AWS_ENDPOINT_URL, config.AWS_EXTERNAL_ENDPOINT)

    logger.info(f"Result ready: {request_id}")
    return response(
        200,
        {
            "request_id": request_id,
            "status": "COMPLETED",
            "audio_url": url,
            "format": fmt,
            "text": text,
        },
    )


def response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, ensure_ascii=False),
    }
