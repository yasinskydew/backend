from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Path, UploadFile, status

from app.api.deps import get_file_service
from app.enums.file_category import FileCategory
from app.schemas.common import ErrorResponse
from app.schemas.file import (
    ConfirmRequest,
    FileResponse,
    PresignRequest,
    PresignResponse,
)
from app.services.file_service import FileService

router = APIRouter(prefix="/files", tags=["files"])


@router.post(
    "",
    response_model=FileResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Empty file or client error"},
        413: {"model": ErrorResponse, "description": "File exceeds max upload size"},
    },
)
async def upload_file(
    file: Annotated[
        UploadFile,
        File(description="Binary file to upload"),
    ],
    category: Annotated[
        FileCategory,
        Form(
            description=(
                "Logical storage category used as object-key prefix "
                "(recipes, avatars, general, categories)"
            ),
        ),
    ],
    file_service: Annotated[FileService, Depends(get_file_service)],
) -> FileResponse:
    """Upload a file via multipart form-data and persist metadata.

    Prefer `/files/presign` + PUT + `/files/confirm` for large client-side
    uploads. Auth planned; currently open. Returns metadata, not a byte stream.
    """
    return await file_service.upload(upload=file, category=category)


@router.post(
    "/presign",
    response_model=PresignResponse,
    status_code=status.HTTP_200_OK,
)
async def presign_upload(
    payload: PresignRequest,
    file_service: Annotated[FileService, Depends(get_file_service)],
) -> PresignResponse:
    """Reserve a `file_id` / `object_key` and return a presigned PUT URL.

    Flow: call this endpoint → PUT the file to `upload_url` with the returned
    `headers` → call `/files/confirm` to persist metadata. The DB row is created
    only on confirm. Auth planned; currently open.
    """
    return await file_service.create_presign(payload)


@router.post(
    "/confirm",
    response_model=FileResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "model": ErrorResponse,
            "description": (
                "object_key/category/file_id mismatch, or uploaded object is empty"
            ),
        },
        404: {
            "model": ErrorResponse,
            "description": "Object not found in storage; upload via presigned URL first",
        },
        409: {
            "model": ErrorResponse,
            "description": "File id or object_key already confirmed / registered",
        },
        413: {"model": ErrorResponse, "description": "File exceeds max upload size"},
    },
)
async def confirm_upload(
    payload: ConfirmRequest,
    file_service: Annotated[FileService, Depends(get_file_service)],
) -> FileResponse:
    """Confirm a completed direct upload after HEAD validates the object exists.

    Requires `file_id` and `object_key` from `/files/presign`. Size and ETag are
    taken from storage HEAD. Auth planned; currently open.
    """
    return await file_service.confirm_upload(payload)


@router.get(
    "/{file_id}",
    response_model=FileResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "File not found"}},
)
async def get_file(
    file_id: Annotated[
        UUID,
        Path(
            description="File unique identifier",
            examples=["550e8400-e29b-41d4-a716-446655440000"],
        ),
    ],
    file_service: Annotated[FileService, Depends(get_file_service)],
) -> FileResponse:
    """Retrieve stored file metadata and public URL by id (does not stream bytes)."""
    return await file_service.get_by_id(file_id)


@router.delete(
    "/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse, "description": "File not found"}},
)
async def delete_file(
    file_id: Annotated[
        UUID,
        Path(
            description="File unique identifier",
            examples=["550e8400-e29b-41d4-a716-446655440000"],
        ),
    ],
    file_service: Annotated[FileService, Depends(get_file_service)],
) -> None:
    """Delete a file from object storage and remove its database record.

    Auth planned; currently open.
    """
    await file_service.delete(file_id)
