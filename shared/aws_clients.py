import boto3
from botocore.config import Config as BotoConfig
from shared.config import config

_boto_config = BotoConfig(
    region_name=config.AWS_REGION,
    retries={"max_attempts": 3, "mode": "standard"},
)

_common_kwargs = {
    "endpoint_url": config.AWS_ENDPOINT_URL,
    "aws_access_key_id": config.AWS_ACCESS_KEY_ID,
    "aws_secret_access_key": config.AWS_SECRET_ACCESS_KEY,
    "config": _boto_config,
}


def get_s3_client():
    return boto3.client("s3", **_common_kwargs)


def get_sqs_client():
    return boto3.client("sqs", **_common_kwargs)


def get_sfn_client():
    return boto3.client("stepfunctions", **_common_kwargs)


def get_transcribe_client():
    return boto3.client("transcribe", **_common_kwargs)


def get_secrets_client():
    return boto3.client("secretsmanager", **_common_kwargs)