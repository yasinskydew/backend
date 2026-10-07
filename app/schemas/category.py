from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SubCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str = Field(..., min_length=1, max_length=64)
    title: str = Field(..., min_length=1, max_length=128)
    sort_order: int = Field(default=0, ge=0)


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str = Field(..., min_length=1, max_length=64)
    title: str = Field(..., min_length=1, max_length=128)
    icon: str = Field(..., min_length=1, max_length=64)
    sort_order: int = Field(default=0, ge=0)
    children: list[SubCategoryResponse] = Field(default_factory=list)
