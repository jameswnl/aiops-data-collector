"""S3 Data storage interface."""

from .s3 import S3Exception, connect, fetch

__all__ = ["S3Exception", "connect", "fetch"]
