from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.api.deps import get_category_service
from app.schemas.category import CategoryResponse
from app.schemas.common import ErrorResponse
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(
    "",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK,
)
async def list_categories(
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> list[CategoryResponse]:
    """List all active categories with nested active subcategories."""
    return await category_service.list_categories()


@router.get(
    "/{slug}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "Category not found"}},
)
async def get_category(
    slug: Annotated[
        str,
        Path(
            min_length=1,
            max_length=64,
            description="URL-friendly category slug",
            examples=["salads"],
        ),
    ],
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryResponse:
    """Retrieve a single active category by slug, including nested subcategories."""
    return await category_service.get_by_slug(slug)
