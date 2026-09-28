import time
import logging
from shared.config import config
from shared.aws_clients import get_dynamodb_client

logger = logging.getLogger(__name__)

dynamodb = get_dynamodb_client()

TTL_SECONDS = 86400  # 24 hrs


def create_request(request_id: str, input_type: str) -> None:
    now = int(time.time())
    try:
        dynamodb.put_item(
            TableName=config.DYNAMODB_REQUESTS_TABLE,
            Item={
                "request_id": {"S": request_id},
                "status": {"S": "IN_PROGRESS"},
                "input_type": {"S": input_type},
                "created_at": {"N": str(now)},
                "updated_at": {"N": str(now)},
                "expires_at": {"N": str(now + TTL_SECONDS)},
            },
        )
        logger.info(f"Created request {request_id}")
    except Exception as e:
        logger.warning(f"Failed to create request {request_id}: {e}")


def mark_completed(request_id: str, s3_key: str, fmt: str) -> None:
    try:
        dynamodb.update_item(
            TableName=config.DYNAMODB_REQUESTS_TABLE,
            Key={"request_id": {"S": request_id}},
            UpdateExpression=(
                "SET #s = :s, s3_key = :k, #f = :f, updated_at = :u"
            ),
            ExpressionAttributeNames={"#s": "status", "#f": "format"},
            ExpressionAttributeValues={
                ":s": {"S": "COMPLETED"},
                ":k": {"S": s3_key},
                ":f": {"S": fmt},
                ":u": {"N": str(int(time.time()))},
            },
        )
        logger.info(f"Marked completed {request_id}")
    except Exception as e:
        logger.warning(f"Failed to mark completed {request_id}: {e}")


def mark_failed(request_id: str, error: str) -> None:
    try:
        dynamodb.update_item(
            TableName=config.DYNAMODB_REQUESTS_TABLE,
            Key={"request_id": {"S": request_id}},
            UpdateExpression="SET #s = :s, #e = :e, updated_at = :u",
            ExpressionAttributeNames={"#s": "status", "#e": "error"},
            ExpressionAttributeValues={
                ":s": {"S": "FAILED"},
                ":e": {"S": error[:1000]},
                ":u": {"N": str(int(time.time()))},
            },
        )
        logger.info(f"Marked failed {request_id}: {error}")
    except Exception as e:
        logger.warning(f"Failed to mark failed {request_id}: {e}")


def get_request(request_id: str) -> dict | None:
    try:
        response = dynamodb.get_item(
            TableName=config.DYNAMODB_REQUESTS_TABLE,
            Key={"request_id": {"S": request_id}},
        )
        return response.get("Item")
    except Exception as e:
        logger.warning(f"Failed to get request {request_id}: {e}")
        return None