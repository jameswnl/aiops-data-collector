import os

import boto3
import botocore

KEY = os.environ.get("AWS_ACCESS_KEY_ID")
SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")

S3 = boto3.client(
    's3',
    aws_access_key_id=KEY,
    aws_secret_access_key=SECRET
)


class S3Exception(Exception):
    """Custom exception for S3 error purposes."""

    pass


def fetch(s3_uri: str) -> None:
    """Collect data from S3 URI."""
    # Download the file
    try:
        data = S3.get_object(Bucket=BUCKET_NAME, Key=s3_uri)
    except botocore.exceptions.ClientError as exception:
        raise S3Exception(exception)

    return data
