"""S3 Data storage interface."""

from .s3 import connect, fetch, list_files

__all__ = ["connect", "fetch", "list_files"]
