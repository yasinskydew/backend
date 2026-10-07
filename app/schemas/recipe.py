from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.enums.home_section import HomeSection
from app.schemas.file import FileResponse


class RecipeCategoryBrief(BaseModel):
    """Minimal category payload nested in recipe responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        ...,
        description="Category unique identifier",
        examples=["11111111-1111-1111-1111-111111111111"],
    )
    slug: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="URL-friendly category slug",
        examples=["salads"],
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Category display title",
        examples=["Salads"],
    )


class RecipeSubCategoryBrief(BaseModel):
    """Minimal subcategory payload nested in recipe responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        ...,
        description="Subcategory unique identifier",
        examples=["22222222-2222-2222-2222-222222222222"],
    )
    slug: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="URL-friendly subcategory slug",
        examples=["warm"],
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Subcategory display title",
        examples=["Warm salads"],
    )


class RecipeCreate(BaseModel):
    """Payload for creating a recipe."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Recipe title",
        examples=["Солянка с грибами"],
    )
    description: str = Field(
        default="",
        description="Recipe description / intro text",
        examples=["Сытный суп с грибами и овощами."],
    )
    category_id: UUID = Field(
        ...,
        description="Parent category id (must exist)",
        examples=["11111111-1111-1111-1111-111111111111"],
    )
    subcategory_id: UUID | None = Field(
        default=None,
        description="Optional subcategory id; must belong to category_id when set",
        examples=["22222222-2222-2222-2222-222222222222"],
    )
    cover_file_id: UUID | None = Field(
        default=None,
        description=(
            "Optional cover image file id from `/files` upload or "
            "`/files/presign` + `/files/confirm`"
        ),
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    likes: int = Field(
        default=0,
        ge=0,
        description="Initial likes counter",
        examples=[12],
    )
    recommends: int | None = Field(
        default=None,
        ge=0,
        description="Optional recommends counter shown on cards",
        examples=[8],
    )
    is_new: bool = Field(
        default=False,
        description="When true, eligible for the new-recipes carousel",
    )
    is_juicy: bool = Field(
        default=False,
        description="When true, eligible for the juiciest section",
    )
    home_section: HomeSection | None = Field(
        default=None,
        description="Optional curated home-page section placement key",
        examples=["vegan-featured"],
    )
    display_category_slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=64,
        description=(
            "Badge category slug when the UI label should differ from "
            "the filter category"
        ),
        examples=["desserts"],
    )


class RecipeUpdate(BaseModel):
    """Partial update payload for a recipe. Only sent fields are applied."""

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="New recipe title",
        examples=["Солянка с грибами (обновлённая)"],
    )
    description: str | None = Field(
        default=None,
        description="New recipe description / intro text",
    )
    category_id: UUID | None = Field(
        default=None,
        description="New parent category id (must exist)",
    )
    subcategory_id: UUID | None = Field(
        default=None,
        description=(
            "New subcategory id; must belong to the resulting category_id. "
            "Send null to clear."
        ),
    )
    cover_file_id: UUID | None = Field(
        default=None,
        description="New cover file id, or null to clear the cover",
    )
    likes: int | None = Field(
        default=None,
        ge=0,
        description="Updated likes counter",
    )
    recommends: int | None = Field(
        default=None,
        ge=0,
        description="Updated recommends counter",
    )
    is_new: bool | None = Field(
        default=None,
        description="Toggle new-recipes carousel eligibility",
    )
    is_juicy: bool | None = Field(
        default=None,
        description="Toggle juiciest-section eligibility",
    )
    home_section: HomeSection | None = Field(
        default=None,
        description="Home section key, or null to clear placement",
        examples=["vegan-quick"],
    )
    display_category_slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=64,
        description="Display badge category slug",
    )


class RecipeResponse(BaseModel):
    """Recipe with nested category, subcategory, and cover file."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        ...,
        description="Recipe unique identifier",
        examples=["33333333-3333-3333-3333-333333333333"],
    )
    title: str = Field(
        ...,
        description="Recipe title",
        examples=["Солянка с грибами"],
    )
    description: str = Field(..., description="Recipe description / intro text")
    category: RecipeCategoryBrief = Field(..., description="Parent category summary")
    subcategory: RecipeSubCategoryBrief | None = Field(
        default=None,
        description="Subcategory summary when set",
    )
    cover_file: FileResponse | None = Field(
        default=None,
        description="Cover image file metadata and public URL, if any",
    )
    likes: int = Field(..., ge=0, description="Likes counter")
    recommends: int | None = Field(
        default=None,
        ge=0,
        description="Recommends counter when set",
    )
    is_new: bool = Field(..., description="Eligible for the new-recipes carousel")
    is_juicy: bool = Field(..., description="Eligible for the juiciest section")
    home_section: HomeSection | None = Field(
        default=None,
        description="Curated home-page section placement key",
        examples=["vegan-featured"],
    )
    display_category_slug: str | None = Field(
        default=None,
        description="Badge category slug when it differs from the filter category",
        examples=["desserts"],
    )
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")
