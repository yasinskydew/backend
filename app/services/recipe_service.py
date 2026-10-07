from uuid import UUID

from app.core.exceptions import AppException, NotFoundError
from app.enums.home_section import HomeSection
from app.models.recipe import Recipe
from app.repositories.category_repository import CategoryRepository
from app.repositories.file_repository import FileRepository
from app.repositories.recipe_repository import RecipeRepository
from app.schemas.file import FileResponse
from app.schemas.recipe import (
    RecipeCategoryBrief,
    RecipeCreate,
    RecipeResponse,
    RecipeSubCategoryBrief,
    RecipeUpdate,
)


class RecipeService:
    def __init__(
        self,
        repository: RecipeRepository,
        category_repository: CategoryRepository,
        file_repository: FileRepository,
    ) -> None:
        self.repository = repository
        self.category_repository = category_repository
        self.file_repository = file_repository

    def _to_response(self, recipe: Recipe) -> RecipeResponse:
        return RecipeResponse(
            id=recipe.id,
            title=recipe.title,
            description=recipe.description,
            category=RecipeCategoryBrief.model_validate(recipe.category),
            subcategory=(
                RecipeSubCategoryBrief.model_validate(recipe.subcategory)
                if recipe.subcategory is not None
                else None
            ),
            cover_file=(
                FileResponse.model_validate(recipe.cover_file)
                if recipe.cover_file is not None
                else None
            ),
            likes=recipe.likes,
            recommends=recipe.recommends,
            is_new=recipe.is_new,
            is_juicy=recipe.is_juicy,
            home_section=(
                HomeSection(recipe.home_section) if recipe.home_section else None
            ),
            display_category_slug=recipe.display_category_slug,
            created_at=recipe.created_at,
            updated_at=recipe.updated_at,
        )

    async def _ensure_category(self, category_id: UUID) -> None:
        category = await self.category_repository.get_by_id(category_id)
        if category is None:
            raise NotFoundError(f"Category '{category_id}' not found")

    async def _ensure_subcategory_belongs(
        self,
        *,
        category_id: UUID,
        subcategory_id: UUID | None,
    ) -> None:
        if subcategory_id is None:
            return
        subcategory = await self.category_repository.get_subcategory_by_id(subcategory_id)
        if subcategory is None:
            raise NotFoundError(f"Subcategory '{subcategory_id}' not found")
        if subcategory.category_id != category_id:
            raise AppException(
                "Subcategory does not belong to the given category",
                status_code=400,
            )

    async def _ensure_cover_file(self, cover_file_id: UUID | None) -> None:
        if cover_file_id is None:
            return
        file_record = await self.file_repository.get_by_id(cover_file_id)
        if file_record is None:
            raise NotFoundError(f"File '{cover_file_id}' not found")

    async def list_recipes(
        self,
        *,
        category_slug: str | None = None,
        subcategory_slug: str | None = None,
        is_new: bool | None = None,
        is_juicy: bool | None = None,
        home_section: HomeSection | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[RecipeResponse]:
        recipes = await self.repository.list(
            category_slug=category_slug,
            subcategory_slug=subcategory_slug,
            is_new=is_new,
            is_juicy=is_juicy,
            home_section=home_section.value if home_section else None,
            limit=limit,
            offset=offset,
        )
        return [self._to_response(recipe) for recipe in recipes]

    async def get_by_id(self, recipe_id: UUID) -> RecipeResponse:
        recipe = await self.repository.get_by_id(recipe_id)
        if recipe is None:
            raise NotFoundError(f"Recipe '{recipe_id}' not found")
        return self._to_response(recipe)

    async def create(self, data: RecipeCreate) -> RecipeResponse:
        await self._ensure_category(data.category_id)
        await self._ensure_subcategory_belongs(
            category_id=data.category_id,
            subcategory_id=data.subcategory_id,
        )
        await self._ensure_cover_file(data.cover_file_id)

        recipe = Recipe(
            title=data.title,
            description=data.description,
            category_id=data.category_id,
            subcategory_id=data.subcategory_id,
            cover_file_id=data.cover_file_id,
            likes=data.likes,
            recommends=data.recommends,
            is_new=data.is_new,
            is_juicy=data.is_juicy,
            home_section=data.home_section.value if data.home_section else None,
            display_category_slug=data.display_category_slug,
        )
        created = await self.repository.create(recipe)
        return self._to_response(created)

    async def update(self, recipe_id: UUID, data: RecipeUpdate) -> RecipeResponse:
        recipe = await self.repository.get_by_id(recipe_id)
        if recipe is None:
            raise NotFoundError(f"Recipe '{recipe_id}' not found")

        payload = data.model_dump(exclude_unset=True)

        category_id = payload.get("category_id", recipe.category_id)
        subcategory_id = payload.get("subcategory_id", recipe.subcategory_id)

        if "category_id" in payload:
            await self._ensure_category(category_id)
        if "category_id" in payload or "subcategory_id" in payload:
            await self._ensure_subcategory_belongs(
                category_id=category_id,
                subcategory_id=subcategory_id,
            )
        if "cover_file_id" in payload:
            await self._ensure_cover_file(payload["cover_file_id"])

        for field, value in payload.items():
            if field == "home_section":
                if value is None:
                    recipe.home_section = None
                elif isinstance(value, HomeSection):
                    recipe.home_section = value.value
                else:
                    recipe.home_section = str(value)
            else:
                setattr(recipe, field, value)

        updated = await self.repository.save(recipe)
        return self._to_response(updated)

    async def delete(self, recipe_id: UUID) -> None:
        recipe = await self.repository.get_by_id(recipe_id)
        if recipe is None:
            raise NotFoundError(f"Recipe '{recipe_id}' not found")
        await self.repository.delete(recipe)
