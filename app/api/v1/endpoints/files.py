from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.api.deps import get_file_service
from app.enums.file_category import FileCategory
from app.schemas.file import FileResponse
from app.services.file_service import FileService

router = APIRouter(prefix="/files", tags=["files"])


@router.post(
    "",
    response_model=FileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file",
)
async def upload_file(
    file: UploadFile = File(...),
    category: FileCategory = Form(...),
    file_service: FileService = Depends(get_file_service),
) -> FileResponse:
    """Upload a file to object storage and persist metadata.

    TODO: require authentication before allowing uploads.
    """
    return await file_service.upload(upload=file, category=category)


@router.get(
    "/{file_id}",
    response_model=FileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get file metadata",
)
async def get_file(
    file_id: UUID,
    file_service: FileService = Depends(get_file_service),
) -> FileResponse:
    """Return file metadata by id, or 404."""
    return await file_service.get_by_id(file_id)


@router.delete(
    "/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a file",
)
async def delete_file(
    file_id: UUID,
    file_service: FileService = Depends(get_file_service),
) -> None:
    """Delete file from storage and database.

    TODO: require authentication before allowing deletes.
    """
    await file_service.delete(file_id)
