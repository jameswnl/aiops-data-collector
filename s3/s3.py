from s3fs import S3FileSystem
from fastparquet import ParquetFile
from pandas import DataFrame


def connect(key: str, secret: str) -> S3FileSystem:
    """Create a Boto3 client for S3 service."""
    filesystem = S3FileSystem(key=key, secret=secret)
    return filesystem


def list_files(filesystem: S3FileSystem, bucket: str, s3_uri: str) -> list:
    """List files on S3 bucket on given URI."""
    # Remove leading and trailing "/"
    s3_uri = s3_uri.strip('/')
    # Find all files on s3_uri in bucket
    paths = filesystem.glob(f'{bucket}/{s3_uri}/*.parquet')

    if paths:
        return paths

    raise FileExistsError(
        f'Bucket {bucket} contains no files matching "{s3_uri}" URI'
    )


def fetch(filesystem: S3FileSystem, bucket: str, s3_uri: str) -> DataFrame:
    """Collect a file from S3 URI."""
    paths = list_files(filesystem, bucket, s3_uri)
    parquet = ParquetFile(paths, open_with=filesystem.open)

    return parquet.to_pandas()
