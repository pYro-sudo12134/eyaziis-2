import json
import logging
from shared.config import config
from shared.aws_clients import get_s3_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = get_s3_client()

def lambda_handler(event, context):
    path_params = event.get("pathParameters") or {}
    request_id = path_params.get("request_id")
    
    if not request_id:
        return response(400, {"error": "request_id is required"})
    
    for fmt in ["mp3", "wav", "ogg"]:
        key = f"{request_id}.{fmt}"
        try:
            s3.head_object(Bucket=config.S3_AUDIO_OUTPUT, Key=key)
        except Exception:
            continue
        
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": config.S3_AUDIO_OUTPUT, "Key": key},
            ExpiresIn=3600,
        )

        if config.AWS_ENDPOINT_URL != config.AWS_EXTERNAL_ENDPOINT:
            url = url.replace(config.AWS_ENDPOINT_URL, config.AWS_EXTERNAL_ENDPOINT)
        
        logger.info(f"Result found: {key}")
        return response(200, {
            "request_id": request_id,
            "status": "COMPLETED",
            "audio_url": url,
            "format": fmt,
        })
    
    return response(200, {
        "request_id": request_id,
        "status": "IN_PROGRESS",
    })


def response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, ensure_ascii=False),
    }