from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Path, UploadFile, status

from app.api.deps import get_file_service
from app.enums.file_category import FileCategory
from app.schemas.common import ErrorResponse
from app.schemas.file import FileResponse
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
    """Upload a file to object storage and persist metadata. Auth planned."""
    return await file_service.upload(upload=file, category=category)


@router.get(
    "/{file_id}",
    response_model=FileResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "File not found"}},
)
async def get_file(
    file_id: Annotated[UUID, Path(description="File unique identifier")],
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
    file_id: Annotated[UUID, Path(description="File unique identifier")],
    file_service: Annotated[FileService, Depends(get_file_service)],
) -> None:
    """Delete a file from object storage and remove its database record. Auth planned."""
    await file_service.delete(file_id)
