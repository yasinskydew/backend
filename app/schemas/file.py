from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.enums.file_category import FileCategory


class PresignRequest(BaseModel):
    """Request a time-limited PUT URL for direct upload to object storage."""

    category: FileCategory = Field(
        ...,
        description=(
            "Logical storage category used as the object-key prefix "
            "(recipes, avatars, general, categories)"
        ),
        examples=["recipes"],
    )
    filename: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Original client filename (sanitized before building object_key)",
        examples=["cover.jpg"],
    )
    content_type: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="MIME type the client must send as Content-Type on the PUT",
        examples=["image/jpeg"],
    )


class PresignResponse(BaseModel):
    """Presigned upload credentials and public URL for the reserved object key."""

    file_id: UUID = Field(
        ...,
        description="Reserved file id; pass unchanged to `/files/confirm`",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    object_key: str = Field(
        ...,
        description="Object key the client must upload to via the presigned URL",
        examples=["recipes/550e8400-e29b-41d4-a716-446655440000_cover.jpg"],
    )
    upload_url: str = Field(
        ...,
        description="Time-limited presigned PUT URL for direct client upload",
        examples=[
            "http://localhost:9000/yee-daa/recipes/550e8400-..._cover.jpg?X-Amz-Algorithm=..."
        ],
    )
    public_url: str = Field(
        ...,
        description="Public URL of the object after a successful upload and confirm",
        examples=[
            "http://localhost:9000/yee-daa/recipes/550e8400-e29b-41d4-a716-446655440000_cover.jpg"
        ],
    )
    expires_in: int = Field(
        ...,
        ge=1,
        description="Presigned URL lifetime in seconds",
        examples=[3600],
    )
    headers: dict[str, str] = Field(
        ...,
        description="Headers the client must include on the PUT request",
        examples=[{"Content-Type": "image/jpeg"}],
    )


class ConfirmRequest(BaseModel):
    """Confirm a completed direct upload and persist file metadata."""

    file_id: UUID = Field(
        ...,
        description="`file_id` returned by `/files/presign`",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    object_key: str = Field(
        ...,
        min_length=1,
        max_length=512,
        description=(
            "`object_key` returned by `/files/presign`; must match "
            "`{category}/{file_id}_*`"
        ),
        examples=["recipes/550e8400-e29b-41d4-a716-446655440000_cover.jpg"],
    )
    original_filename: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Original client filename stored in metadata",
        examples=["cover.jpg"],
    )
    content_type: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="MIME type of the uploaded object",
        examples=["image/jpeg"],
    )
    category: FileCategory = Field(
        ...,
        description=(
            "Logical storage category; must match the object_key prefix "
            "from `/files/presign`"
        ),
        examples=["recipes"],
    )


class FileResponse(BaseModel):
    """Stored file metadata and public URL."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        ...,
        description="File unique identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
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
        examples=["yee-daa"],
    )
    original_filename: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Original client filename before sanitization",
        examples=["cover.jpg"],
    )
    content_type: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="MIME type of the uploaded file",
        examples=["image/jpeg"],
    )
    size: int = Field(
        ...,
        ge=0,
        description="File size in bytes (from upload body or storage HEAD)",
        examples=[204800],
    )
    category: FileCategory = Field(
        ...,
        description="Logical storage category used as the object-key prefix",
        examples=["recipes"],
    )
    url: str = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="Public URL to access the object",
        examples=[
            "http://localhost:9000/yee-daa/recipes/550e8400-e29b-41d4-a716-446655440000_photo.jpg"
        ],
    )
    etag: str | None = Field(
        default=None,
        max_length=128,
        description="Storage provider ETag, if available",
    )
    created_at: datetime = Field(..., description="Record creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")
