from app.core.config import Settings
from app.storage.base import StorageProvider
from app.storage.minio_provider import MinioProvider
from app.storage.s3_provider import S3Provider


class StorageFactory:
    @staticmethod
    def create(settings: Settings) -> StorageProvider:
        provider = settings.storage_provider.strip().lower()
        if provider == "minio":
            return MinioProvider(settings)
        if provider == "s3":
            return S3Provider(settings)
        raise ValueError(
            f"Unsupported STORAGE_PROVIDER '{settings.storage_provider}'. "
            "Expected 'minio' or 's3'."
        )
