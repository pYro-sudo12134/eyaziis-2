import logging
import boto3
from botocore.config import Config as BotoConfig
from shared.config import config

logger = logging.getLogger(__name__)

_boto_config = BotoConfig(
    region_name=config.AWS_REGION,
    retries={"max_attempts": 3, "mode": "standard"},
)

_cache = {}


def get_parameter(name: str) -> str:
    """Читает SSM-параметр с кешированием."""
    if name in _cache:
        return _cache[name]
    
    client = boto3.client(
        "ssm",
        endpoint_url=config.AWS_ENDPOINT_URL,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        config=_boto_config,
    )
    response = client.get_parameter(Name=name, WithDecryption=True)
    value = response["Parameter"]["Value"]
    _cache[name] = value
    logger.info(f"Loaded SSM parameter: {name}")
    return value


def get_state_machine_arn() -> str:
    return get_parameter(config.STATE_MACHINE_ARN_PARAM)