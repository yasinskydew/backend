from app.core.exceptions import NotFoundError
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryResponse, SubCategoryResponse


class CategoryService:
    def __init__(self, repository: CategoryRepository) -> None:
        self.repository = repository

    def _to_response(self, category: Category) -> CategoryResponse:
        children = sorted(
            category.subcategories,
            key=lambda item: (item.sort_order, item.title),
        )
        return CategoryResponse(
            id=category.id,
            slug=category.slug,
            title=category.title,
            icon=category.icon,
            sort_order=category.sort_order,
            children=[
                SubCategoryResponse(
                    id=child.id,
                    slug=child.slug,
                    title=child.title,
                    sort_order=child.sort_order,
                )
                for child in children
                if child.is_active
            ],
        )

    async def list_categories(self) -> list[CategoryResponse]:
        categories = await self.repository.get_all_active()
        return [self._to_response(category) for category in categories]

    async def get_by_slug(self, slug: str) -> CategoryResponse:
        category = await self.repository.get_by_slug(slug)
        if category is None:
            raise NotFoundError(f"Category '{slug}' not found")
        return self._to_response(category)
