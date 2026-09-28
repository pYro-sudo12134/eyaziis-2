import json
import logging
from shared.config import config
from shared.aws_clients import get_sfn_client
from shared.ssm import get_state_machine_arn
from shared.requests_db import mark_failed

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sfn = get_sfn_client()


def lambda_handler(event, context):
    logger.info(f"Received {len(event.get('Records', []))} records")

    state_machine_arn = get_state_machine_arn()

    for record in event["Records"]:
        message = json.loads(record["body"])
        request_id = message.get("request_id", "unknown")

        logger.info(f"Dispatching request_id={request_id}")

        try:
            sfn.start_execution(
                stateMachineArn=state_machine_arn,
                name=request_id,
                input=json.dumps(message, ensure_ascii=False),
            )
        except sfn.exceptions.ExecutionAlreadyExists:
            logger.warning(f"Execution {request_id} already exists, skipping")
        except Exception as e:
            logger.exception(f"Failed to start execution for {request_id}")
            mark_failed(request_id, str(e))
            raise

    return {"status": "ok"}
