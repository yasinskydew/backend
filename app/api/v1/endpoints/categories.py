from fastapi import APIRouter, Depends, status

from app.api.deps import get_category_service
from app.schemas.category import CategoryResponse
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(
    "",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="List categories",
)
async def list_categories(
    category_service: CategoryService = Depends(get_category_service),
) -> list[CategoryResponse]:
    """Return all active categories with nested subcategories."""
    return await category_service.list_categories()


@router.get(
    "/{slug}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get category by slug",
)
async def get_category(
    slug: str,
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    """Return a single active category by slug, or 404."""
    return await category_service.get_by_slug(slug)
