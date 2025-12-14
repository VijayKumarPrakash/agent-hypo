"""Cloud storage utility for uploading analysis outputs to S3-compatible storage.

Supports AWS S3, Cloudflare R2, MinIO, and other S3-compatible services.
"""

import os
import logging
from pathlib import Path
from typing import Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)


class StorageUploader:
    """Handles uploading files to S3-compatible cloud storage."""

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        region: Optional[str] = None,
        public_url_base: Optional[str] = None
    ):
        """Initialize S3 storage uploader.

        Args:
            bucket_name: S3 bucket name (or S3_BUCKET env var)
            endpoint_url: Custom endpoint URL for S3-compatible services like R2, MinIO
                         (or S3_ENDPOINT_URL env var). Leave None for AWS S3.
            access_key_id: AWS access key (or S3_ACCESS_KEY_ID env var)
            secret_access_key: AWS secret key (or S3_SECRET_ACCESS_KEY env var)
            region: AWS region (or S3_REGION env var, defaults to us-east-1)
            public_url_base: Base URL for constructing public URLs
                            (or S3_PUBLIC_URL_BASE env var)
        """
        self.bucket_name = bucket_name or os.getenv("S3_BUCKET")
        self.endpoint_url = endpoint_url or os.getenv("S3_ENDPOINT_URL")
        self.access_key_id = access_key_id or os.getenv("S3_ACCESS_KEY_ID")
        self.secret_access_key = secret_access_key or os.getenv("S3_SECRET_ACCESS_KEY")
        self.region = region or os.getenv("S3_REGION", "us-east-1")
        self.public_url_base = public_url_base or os.getenv("S3_PUBLIC_URL_BASE")

        if not self.bucket_name:
            raise ValueError(
                "S3_BUCKET must be provided via parameter or S3_BUCKET environment variable"
            )

        if not self.access_key_id or not self.secret_access_key:
            raise ValueError(
                "S3 credentials must be provided via parameters or "
                "S3_ACCESS_KEY_ID and S3_SECRET_ACCESS_KEY environment variables"
            )

        # Initialize S3 client
        session_config = {
            "aws_access_key_id": self.access_key_id,
            "aws_secret_access_key": self.secret_access_key,
            "region_name": self.region,
        }

        if self.endpoint_url:
            session_config["endpoint_url"] = self.endpoint_url
            logger.info(f"Using custom S3 endpoint: {self.endpoint_url}")

        try:
            self.s3_client = boto3.client("s3", **session_config)
            logger.info(f"S3 client initialized for bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise

        # Determine public URL base if not provided
        if not self.public_url_base:
            if self.endpoint_url:
                # For custom endpoints (like R2), construct from endpoint
                self.public_url_base = f"{self.endpoint_url}/{self.bucket_name}"
            else:
                # For AWS S3
                self.public_url_base = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com"

        logger.info(f"Public URL base: {self.public_url_base}")

    def upload_file(
        self,
        file_content: bytes,
        s3_key: str,
        content_type: str = "application/octet-stream"
    ) -> str:
        """Upload a file to S3 and return its public URL.

        Args:
            file_content: File content as bytes
            s3_key: S3 key (path) for the file
            content_type: MIME type of the file

        Returns:
            Public URL to the uploaded file

        Raises:
            Exception: If upload fails
        """
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                # Make file publicly readable (adjust ACL based on your bucket policy)
                # ACL='public-read'  # Uncomment if needed
            )

            public_url = f"{self.public_url_base}/{s3_key}"
            logger.info(f"Uploaded file to: {public_url}")
            return public_url

        except NoCredentialsError:
            logger.error("S3 credentials not available")
            raise Exception("S3 credentials not configured")
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise Exception(f"Failed to upload to S3: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {e}")
            raise

    def upload_text_file(self, text_content: str, s3_key: str, content_type: str = "text/plain") -> str:
        """Upload text content to S3.

        Args:
            text_content: Text content as string
            s3_key: S3 key (path) for the file
            content_type: MIME type (defaults to text/plain)

        Returns:
            Public URL to the uploaded file
        """
        return self.upload_file(
            file_content=text_content.encode("utf-8"),
            s3_key=s3_key,
            content_type=content_type
        )

    def upload_json_file(self, json_content: str, s3_key: str) -> str:
        """Upload JSON content to S3.

        Args:
            json_content: JSON string
            s3_key: S3 key (path) for the file

        Returns:
            Public URL to the uploaded file
        """
        return self.upload_text_file(
            text_content=json_content,
            s3_key=s3_key,
            content_type="application/json"
        )

    @staticmethod
    def is_configured() -> bool:
        """Check if S3 storage is properly configured via environment variables.

        Returns:
            True if all required S3 environment variables are set
        """
        required_vars = ["S3_BUCKET", "S3_ACCESS_KEY_ID", "S3_SECRET_ACCESS_KEY"]
        return all(os.getenv(var) for var in required_vars)


def get_content_type(filename: str) -> str:
    """Determine content type from filename extension.

    Args:
        filename: Filename or path

    Returns:
        MIME type string
    """
    extension = Path(filename).suffix.lower()
    content_types = {
        ".md": "text/markdown",
        ".txt": "text/plain",
        ".json": "application/json",
        ".csv": "text/csv",
        ".py": "text/x-python",
        ".html": "text/html",
        ".xml": "application/xml",
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }
    return content_types.get(extension, "application/octet-stream")
