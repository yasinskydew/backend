from __future__ import annotations

import re
import uuid
from pathlib import PurePosixPath

from fastapi import UploadFile

from app.core.config import Settings
from app.core.exceptions import AppException, NotFoundError
from app.enums.file_category import FileCategory
from app.models.file import File
from app.repositories.file_repository import FileRepository
from app.schemas.file import FileResponse
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
