from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.repositories.category_repository import CategoryRepository
from app.repositories.file_repository import FileRepository
from app.repositories.recipe_repository import RecipeRepository
from app.services.category_service import CategoryService
from app.services.file_service import FileService
from app.services.recipe_service import RecipeService
from app.storage.base import StorageProvider
from app.storage.factory import StorageFactory


async def get_category_repository(
    session: AsyncSession = Depends(get_db),
) -> AsyncGenerator[CategoryRepository, None]:
    yield CategoryRepository(session)


async def get_category_service(
    repository: CategoryRepository = Depends(get_category_repository),
) -> CategoryService:
    return CategoryService(repository)


def get_storage_provider(
    settings: Settings = Depends(get_settings),
) -> StorageProvider:
    return StorageFactory.create(settings)


async def get_file_repository(
    session: AsyncSession = Depends(get_db),
) -> AsyncGenerator[FileRepository, None]:
    yield FileRepository(session)


async def get_file_service(
    repository: FileRepository = Depends(get_file_repository),
    storage: StorageProvider = Depends(get_storage_provider),
    settings: Settings = Depends(get_settings),
) -> FileService:
    return FileService(repository, storage, settings)


async def get_recipe_repository(
    session: AsyncSession = Depends(get_db),
) -> AsyncGenerator[RecipeRepository, None]:
    yield RecipeRepository(session)


async def get_recipe_service(
    repository: RecipeRepository = Depends(get_recipe_repository),
    category_repository: CategoryRepository = Depends(get_category_repository),
    file_repository: FileRepository = Depends(get_file_repository),
) -> RecipeService:
    return RecipeService(repository, category_repository, file_repository)
