from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.models.recipe import Recipe
from app.models.subcategory import SubCategory


class RecipeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _base_query(self) -> Select[tuple[Recipe]]:
        return select(Recipe).options(
            selectinload(Recipe.category),
            selectinload(Recipe.subcategory),
            selectinload(Recipe.cover_file),
        )

    async def list(
        self,
        *,
        category_slug: str | None = None,
        subcategory_slug: str | None = None,
        is_new: bool | None = None,
        is_juicy: bool | None = None,
        home_section: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Recipe]:
        stmt = self._base_query()

        if category_slug is not None:
            stmt = stmt.join(Recipe.category).where(Category.slug == category_slug)
        if subcategory_slug is not None:
            stmt = stmt.join(Recipe.subcategory).where(
                SubCategory.slug == subcategory_slug,
            )
        if is_new is not None:
            stmt = stmt.where(Recipe.is_new.is_(is_new))
        if is_juicy is not None:
            stmt = stmt.where(Recipe.is_juicy.is_(is_juicy))
        if home_section is not None:
            stmt = stmt.where(Recipe.home_section == home_section)

        stmt = (
            stmt.order_by(Recipe.created_at.desc(), Recipe.title)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_by_id(self, recipe_id: UUID) -> Recipe | None:
        stmt = self._base_query().where(Recipe.id == recipe_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_title(self, title: str) -> Recipe | None:
        """Fetch first recipe by exact title (for seeding upserts)."""
        stmt = self._base_query().where(Recipe.title == title).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, recipe: Recipe) -> Recipe:
        self.session.add(recipe)
        await self.session.flush()
        return await self.get_by_id(recipe.id)  # type: ignore[return-value]

    async def save(self, recipe: Recipe) -> Recipe:
        await self.session.flush()
        return await self.get_by_id(recipe.id)  # type: ignore[return-value]

    async def delete(self, recipe: Recipe) -> None:
        await self.session.delete(recipe)
        await self.session.flush()
