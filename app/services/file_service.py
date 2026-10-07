from __future__ import annotations

import re
import uuid
from pathlib import PurePosixPath

from fastapi import UploadFile

from app.core.config import Settings
from app.core.exceptions import AppException, ConflictError, NotFoundError
from app.enums.file_category import FileCategory
from app.models.file import File
from app.repositories.file_repository import FileRepository
from app.schemas.file import (
    ConfirmRequest,
    FileResponse,
    PresignRequest,
    PresignResponse,
)
from app.storage.base import StorageProvider

_UNSAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


class FileService:
    def __init__(
        self,
        repository: FileRepository,
        storage: StorageProvider,
        settings: Settings,
    ) -> None:
        self.repository = repository
        self.storage = storage
        self.settings = settings

    def _to_response(self, file_record: File) -> FileResponse:
        return FileResponse.model_validate(file_record)

    @staticmethod
    def sanitize_filename(filename: str | None) -> str:
        raw = (filename or "").strip() or "file"
        name = PurePosixPath(raw.replace("\\", "/")).name
        name = name.replace(" ", "_")
        name = _UNSAFE_FILENAME_RE.sub("_", name).strip("._")
        if not name:
            name = "file"
        return name[:200]

    def _build_object_key(
        self,
        *,
        category: FileCategory,
        file_id: uuid.UUID,
        sanitized_filename: str,
    ) -> str:
        return f"{category.value}/{file_id}_{sanitized_filename}"

    async def upload(
        self,
        *,
        upload: UploadFile,
        category: FileCategory,
    ) -> FileResponse:
        data = await upload.read()
        size = len(data)
        if size == 0:
            raise AppException("Uploaded file is empty", status_code=400)
        if size > self.settings.storage_max_upload_bytes:
            raise AppException(
                f"File exceeds max upload size of "
                f"{self.settings.storage_max_upload_bytes} bytes",
                status_code=413,
            )

        file_id = uuid.uuid4()
        original_filename = upload.filename or "file"
        sanitized_filename = self.sanitize_filename(original_filename)
        object_key = self._build_object_key(
            category=category,
            file_id=file_id,
            sanitized_filename=sanitized_filename,
        )
        content_type = upload.content_type or "application/octet-stream"

        etag = await self.storage.upload(
            object_key=object_key,
            data=data,
            content_type=content_type,
        )
        url = self.storage.build_public_url(object_key)

        try:
            file_record = await self.repository.create(
                file_id=file_id,
                object_key=object_key,
                bucket=self.settings.storage_bucket,
                original_filename=original_filename[:255],
                content_type=content_type[:128],
                size=size,
                category=category.value,
                url=url,
                etag=etag or None,
            )
        except Exception:
            await self.storage.delete(object_key=object_key)
            raise

        return self._to_response(file_record)

    async def create_presign(self, data: PresignRequest) -> PresignResponse:
        file_id = uuid.uuid4()
        sanitized_filename = self.sanitize_filename(data.filename)
        object_key = self._build_object_key(
            category=data.category,
            file_id=file_id,
            sanitized_filename=sanitized_filename,
        )
        expires_in = self.settings.storage_presign_expire_seconds
        upload_url = await self.storage.create_presigned_put_url(
            object_key=object_key,
            content_type=data.content_type,
            expires_in=expires_in,
        )
        return PresignResponse(
            file_id=file_id,
            object_key=object_key,
            upload_url=upload_url,
            public_url=self.storage.build_public_url(object_key),
            expires_in=expires_in,
            headers={"Content-Type": data.content_type},
        )

    async def confirm_upload(self, data: ConfirmRequest) -> FileResponse:
        existing_by_id = await self.repository.get_by_id(data.file_id)
        if existing_by_id is not None:
            raise ConflictError(f"File '{data.file_id}' already exists")

        existing_by_key = await self.repository.get_by_object_key(data.object_key)
        if existing_by_key is not None:
            raise ConflictError(f"Object key '{data.object_key}' already registered")

        expected_prefix = f"{data.category.value}/"
        if not data.object_key.startswith(expected_prefix):
            raise AppException(
                "object_key does not match the given category",
                status_code=400,
            )
        if not data.object_key.startswith(f"{data.category.value}/{data.file_id}_"):
            raise AppException(
                "object_key does not match the given file_id",
                status_code=400,
            )

        head = await self.storage.head_object(object_key=data.object_key)
        if head is None:
            raise NotFoundError(
                f"Object '{data.object_key}' not found in storage; upload first",
            )
        if head.size <= 0:
            raise AppException("Uploaded object is empty", status_code=400)
        if head.size > self.settings.storage_max_upload_bytes:
            raise AppException(
                f"File exceeds max upload size of "
                f"{self.settings.storage_max_upload_bytes} bytes",
                status_code=413,
            )

        file_record = await self.repository.create(
            file_id=data.file_id,
            object_key=data.object_key,
            bucket=self.settings.storage_bucket,
            original_filename=data.original_filename[:255],
            content_type=data.content_type[:128],
            size=head.size,
            category=data.category.value,
            url=self.storage.build_public_url(data.object_key),
            etag=head.etag,
        )
        return self._to_response(file_record)

    async def get_by_id(self, file_id: uuid.UUID) -> FileResponse:
        file_record = await self.repository.get_by_id(file_id)
        if file_record is None:
            raise NotFoundError(f"File '{file_id}' not found")
        return self._to_response(file_record)

    async def delete(self, file_id: uuid.UUID) -> None:
        file_record = await self.repository.get_by_id(file_id)
        if file_record is None:
            raise NotFoundError(f"File '{file_id}' not found")

        # Storage first; 404 on storage is treated as success (orphan cleanup).
        await self.storage.delete(object_key=file_record.object_key)
        await self.repository.delete(file_record)
