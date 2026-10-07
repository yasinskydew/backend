from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File


class FileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, file_id: UUID) -> File | None:
        stmt = select(File).where(File.id == file_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_object_key(self, object_key: str) -> File | None:
        stmt = select(File).where(File.object_key == object_key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        file_id: UUID,
        object_key: str,
        bucket: str,
        original_filename: str,
        content_type: str,
        size: int,
        category: str,
        url: str,
        etag: str | None,
    ) -> File:
        file_record = File(
            id=file_id,
            object_key=object_key,
            bucket=bucket,
            original_filename=original_filename,
            content_type=content_type,
            size=size,
            category=category,
            url=url,
            etag=etag,
        )
        self.session.add(file_record)
        await self.session.flush()
        await self.session.refresh(file_record)
        return file_record

    async def delete(self, file_record: File) -> None:
        await self.session.delete(file_record)
        await self.session.flush()
