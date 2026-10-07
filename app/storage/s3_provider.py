from botocore.config import Config
from botocore.exceptions import ClientError

import aioboto3

from app.core.config import Settings
from app.storage.base import StorageProvider


class S3Provider(StorageProvider):
    def __init__(self, settings: Settings) -> None:
        self._bucket = settings.storage_bucket
        self._public_base_url = settings.storage_public_base_url.rstrip("/")
        self._session = aioboto3.Session()
        addressing_style = "path" if settings.storage_force_path_style else "auto"
        self._client_kwargs: dict = {
            "service_name": "s3",
            "aws_access_key_id": settings.storage_access_key,
            "aws_secret_access_key": settings.storage_secret_key,
            "region_name": settings.storage_region,
            "config": Config(s3={"addressing_style": addressing_style}),
        }
        if settings.storage_endpoint_url:
            self._client_kwargs["endpoint_url"] = settings.storage_endpoint_url

    async def upload(
        self,
        *,
        object_key: str,
        data: bytes,
        content_type: str,
    ) -> str:
        async with self._session.client(**self._client_kwargs) as client:
            response = await client.put_object(
                Bucket=self._bucket,
                Key=object_key,
                Body=data,
                ContentType=content_type,
            )
        etag = response.get("ETag") or ""
        return str(etag).strip('"')

    async def delete(self, *, object_key: str) -> None:
        try:
            async with self._session.client(**self._client_kwargs) as client:
                await client.delete_object(Bucket=self._bucket, Key=object_key)
        except ClientError as exc:
            code = str(exc.response.get("Error", {}).get("Code", ""))
            if code in {"404", "NoSuchKey", "NotFound", "NoSuchBucket"}:
                return
            raise

    def build_public_url(self, object_key: str) -> str:
        return f"{self._public_base_url}/{object_key.lstrip('/')}"
