from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.models.subcategory import SubCategory


class CategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all_active(self) -> list[Category]:
        stmt = (
            select(Category)
            .where(Category.is_active.is_(True))
            .options(selectinload(Category.subcategories))
            .order_by(Category.sort_order, Category.title)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_by_slug(self, slug: str) -> Category | None:
        stmt = (
            select(Category)
            .where(Category.slug == slug, Category.is_active.is_(True))
            .options(selectinload(Category.subcategories))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, category_id: UUID) -> Category | None:
        stmt = (
            select(Category)
            .where(Category.id == category_id)
            .options(selectinload(Category.subcategories))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug_any(self, slug: str) -> Category | None:
        """Fetch category by slug regardless of is_active (for seeding)."""
        stmt = (
            select(Category)
            .where(Category.slug == slug)
            .options(selectinload(Category.subcategories))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_category(
        self,
        *,
        slug: str,
        title: str,
        icon: str,
        sort_order: int,
        is_active: bool = True,
    ) -> Category:
        category = await self.get_by_slug_any(slug)
        if category is None:
            category = Category(
                slug=slug,
                title=title,
                icon=icon,
                sort_order=sort_order,
                is_active=is_active,
            )
            self.session.add(category)
        else:
            category.title = title
            category.icon = icon
            category.sort_order = sort_order
            category.is_active = is_active
        await self.session.flush()
        return category

    async def upsert_subcategory(
        self,
        *,
        category_id: UUID,
        slug: str,
        title: str,
        sort_order: int,
        is_active: bool = True,
    ) -> SubCategory:
        stmt = select(SubCategory).where(
            SubCategory.category_id == category_id,
            SubCategory.slug == slug,
        )
        result = await self.session.execute(stmt)
        subcategory = result.scalar_one_or_none()

        if subcategory is None:
            subcategory = SubCategory(
                category_id=category_id,
                slug=slug,
                title=title,
                sort_order=sort_order,
                is_active=is_active,
            )
            self.session.add(subcategory)
        else:
            subcategory.title = title
            subcategory.sort_order = sort_order
            subcategory.is_active = is_active

        await self.session.flush()
        return subcategory
