from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import get_recipe_service
from app.enums.home_section import HomeSection
from app.schemas.common import ErrorResponse
from app.schemas.recipe import RecipeCreate, RecipeResponse, RecipeUpdate
from app.services.recipe_service import RecipeService

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get(
    "",
    response_model=list[RecipeResponse],
    status_code=status.HTTP_200_OK,
)
async def list_recipes(
    recipe_service: Annotated[RecipeService, Depends(get_recipe_service)],
    category_slug: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=64,
            description="Filter by parent category slug",
            examples=["salads"],
        ),
    ] = None,
    subcategory_slug: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=64,
            description="Filter by subcategory slug",
            examples=["warm"],
        ),
    ] = None,
    is_new: Annotated[
        bool | None,
        Query(description="When set, filter by the new-recipes carousel flag"),
    ] = None,
    is_juicy: Annotated[
        bool | None,
        Query(description="When set, filter by the juiciest-section flag"),
    ] = None,
    home_section: Annotated[
        HomeSection | None,
        Query(
            description="Filter by curated home-page section key",
            examples=["vegan-featured"],
        ),
    ] = None,
    limit: Annotated[
        int,
        Query(ge=1, le=100, description="Maximum number of recipes to return (max 100)"),
    ] = 20,
    offset: Annotated[
        int,
        Query(ge=0, description="Number of recipes to skip for offset pagination"),
    ] = 0,
) -> list[RecipeResponse]:
    """List recipes with optional filters and offset pagination.

    Filters are combined with AND. Nested `category`, `subcategory`, and
    `cover_file` are included when present. Auth is not required for read.
    """
    return await recipe_service.list_recipes(
        category_slug=category_slug,
        subcategory_slug=subcategory_slug,
        is_new=is_new,
        is_juicy=is_juicy,
        home_section=home_section,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "Recipe not found"}},
)
async def get_recipe(
    recipe_id: Annotated[
        UUID,
        Path(
            description="Recipe unique identifier",
            examples=["33333333-3333-3333-3333-333333333333"],
        ),
    ],
    recipe_service: Annotated[RecipeService, Depends(get_recipe_service)],
) -> RecipeResponse:
    """Retrieve a single recipe by id with nested category, subcategory, and cover."""
    return await recipe_service.get_by_id(recipe_id)


@router.post(
    "",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Subcategory does not belong to the given category",
        },
        404: {
            "model": ErrorResponse,
            "description": "Category, subcategory, or cover file not found",
        },
    },
)
async def create_recipe(
    payload: RecipeCreate,
    recipe_service: Annotated[RecipeService, Depends(get_recipe_service)],
) -> RecipeResponse:
    """Create a recipe linked to an existing category and optional cover file.

    Auth planned; currently open.
    """
    return await recipe_service.create(payload)


@router.patch(
    "/{recipe_id}",
    response_model=RecipeResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Subcategory does not belong to the given category",
        },
        404: {
            "model": ErrorResponse,
            "description": "Recipe, category, subcategory, or cover file not found",
        },
    },
)
async def update_recipe(
    recipe_id: Annotated[
        UUID,
        Path(
            description="Recipe unique identifier",
            examples=["33333333-3333-3333-3333-333333333333"],
        ),
    ],
    payload: RecipeUpdate,
    recipe_service: Annotated[RecipeService, Depends(get_recipe_service)],
) -> RecipeResponse:
    """Partially update a recipe. Only fields present in the body are applied.

    Auth planned; currently open.
    """
    return await recipe_service.update(recipe_id, payload)


@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse, "description": "Recipe not found"}},
)
async def delete_recipe(
    recipe_id: Annotated[
        UUID,
        Path(
            description="Recipe unique identifier",
            examples=["33333333-3333-3333-3333-333333333333"],
        ),
    ],
    recipe_service: Annotated[RecipeService, Depends(get_recipe_service)],
) -> None:
    """Delete a recipe by id. Does not delete the linked cover file object.

    Auth planned; currently open.
    """
    await recipe_service.delete(recipe_id)
