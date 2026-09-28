import json
import logging
import requests
from shared.config import config
from shared.aws_clients import get_s3_client, get_sqs_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = get_s3_client()
sqs = get_sqs_client()


def lambda_handler(event, context):
    logger.info(f"TTS: {len(event.get('Records', []))} records")
    
    for record in event["Records"]:
        message = json.loads(record["body"])
        process(message)
    
    return {"status": "ok"}


def process(message):
    text = message["text"]
    request_id = message["request_id"]
    
    logger.info(f"TTS: request_id={request_id}, len={len(text)}")
    
    response = requests.post(
        f"{config.TTS_SERVICE_URL}/synthesize",
        json={
            "text": text,
            "voice": message.get("voice", "ru_RU-irina-medium"),
            "speed": message.get("speed", 1.0),
            "volume": message.get("volume", 1.0),
            "pitch": message.get("pitch", 1.0),
            "format": message.get("format", "mp3"),
        },
        timeout=60,
    )
    response.raise_for_status()
    audio_bytes = response.content
    
    fmt = message.get("format", "mp3")
    s3_key = f"{request_id}.{fmt}"
    
    s3.put_object(
        Bucket=config.S3_AUDIO_OUTPUT,
        Key=s3_key,
        Body=audio_bytes,
        ContentType=f"audio/{fmt}",
    )
    
    logger.info(f"TTS done: s3://{config.S3_AUDIO_OUTPUT}/{s3_key}, size={len(audio_bytes)}")
    
    sqs.send_message(
        QueueUrl=config.SQS_OUTPUT_URL,
        MessageBody=json.dumps({
            "request_id": request_id,
            "status": "COMPLETED",
            "s3_key": s3_key,
            "bucket": config.S3_AUDIO_OUTPUT,
            "format": fmt,
        }),
    )