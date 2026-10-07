from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.enums.file_category import FileCategory


class FileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    object_key: str = Field(..., min_length=1, max_length=512)
    bucket: str = Field(..., min_length=1, max_length=128)
    original_filename: str = Field(..., min_length=1, max_length=255)
    content_type: str = Field(..., min_length=1, max_length=128)
    size: int = Field(..., ge=0)
    category: FileCategory
    url: str = Field(..., min_length=1, max_length=1024)
    etag: str | None = Field(default=None, max_length=128)
    created_at: datetime
    updated_at: datetime
