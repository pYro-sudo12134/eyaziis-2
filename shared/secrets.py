import json
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


def get_secret(secret_name: str) -> dict:
    """Читает секрет из Secrets Manager с кешированием."""
    if not config.SECRETS_MANAGER_ENABLED:
        logger.info(f"Secrets Manager disabled, skipping: {secret_name}")
        return {}

    if secret_name in _cache:
        return _cache[secret_name]

    try:
        client = boto3.client(
            "secretsmanager",
            endpoint_url=config.AWS_ENDPOINT_URL,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            config=_boto_config,
        )
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response["SecretString"])
        _cache[secret_name] = secret
        logger.info(f"Loaded secret: {secret_name}")
        return secret
    except Exception as e:
        logger.warning(f"Failed to load secret {secret_name}: {e}")
        return {}


def get_qdrant_api_key() -> str:
    """Возвращает Qdrant API key из Secrets Manager, если он есть."""
    if not config.QDRANT_API_KEY_SECRET:
        return ""
    secret = get_secret(config.QDRANT_API_KEY_SECRET)
    return secret.get("api_key", "")
