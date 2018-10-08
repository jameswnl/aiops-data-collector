import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError


class S3Exception(Exception):
    """Custom exception for S3 error purposes."""

    pass


def connect(key: str, secret: str) -> BaseClient:
    """Create a Boto3 client for S3 service."""
    client = boto3.client(
        's3',
        aws_access_key_id=key,
        aws_secret_access_key=secret
    )
    return client


def fetch(client: BaseClient, bucket: str, s3_uri: str) -> None:
    """Collect a file from S3 URI."""
    # Download the file
    try:
        data = client.get_object(Bucket=bucket, Key=s3_uri)
    except ClientError as exception:
        raise S3Exception(exception)

    return data
