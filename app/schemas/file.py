from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.enums.file_category import FileCategory


class FileResponse(BaseModel):
    """Stored file metadata and public URL."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="File unique identifier")
    object_key: str = Field(
        ...,
        min_length=1,
        max_length=512,
        description="Object key in the storage bucket",
        examples=["recipes/550e8400-e29b-41d4-a716-446655440000_photo.jpg"],
    )
    bucket: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Storage bucket name",
    )
    original_filename: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Original client filename before sanitization",
    )
    content_type: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="MIME type of the uploaded file",
        examples=["image/jpeg"],
    )
    size: int = Field(..., ge=0, description="File size in bytes")
    category: FileCategory = Field(
        ...,
        description="Logical storage category used as the object-key prefix",
    )
    url: str = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="Public URL to access the object",
    )
    etag: str | None = Field(
        default=None,
        max_length=128,
        description="Storage provider ETag, if available",
    )
    created_at: datetime = Field(..., description="Record creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")
