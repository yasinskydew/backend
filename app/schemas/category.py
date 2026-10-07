from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SubCategoryResponse(BaseModel):
    """Nested subcategory under a parent category."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Subcategory unique identifier")
    slug: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="URL-friendly subcategory slug",
        examples=["breakfast"],
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Display title",
        examples=["Breakfast"],
    )
    sort_order: int = Field(
        default=0,
        ge=0,
        description="Display order within the parent category (ascending)",
    )


class CategoryResponse(BaseModel):
    """Active category with nested active subcategories."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Category unique identifier")
    slug: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="URL-friendly category slug",
        examples=["meals"],
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Display title",
        examples=["Meals"],
    )
    icon: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Icon key or asset identifier for the client UI",
        examples=["utensils"],
    )
    sort_order: int = Field(
        default=0,
        ge=0,
        description="Display order among top-level categories (ascending)",
    )
    children: list[SubCategoryResponse] = Field(
        default_factory=list,
        description="Active subcategories sorted by sort_order, then title",
    )
