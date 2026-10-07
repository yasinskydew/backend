"""Idempotent upsert of recipes from scripts/data/recipes.json."""

from __future__ import annotations

import asyncio
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path, PurePosixPath

# Ensure backend root is on sys.path when run as a script
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.models.recipe import Recipe
from app.repositories.category_repository import CategoryRepository
from app.repositories.file_repository import FileRepository
from app.repositories.recipe_repository import RecipeRepository

RECIPES_JSON = Path(__file__).resolve().parent / "data" / "recipes.json"


def load_recipes() -> list[dict]:
    if not RECIPES_JSON.exists():
        raise FileNotFoundError(f"Recipes JSON not found: {RECIPES_JSON}")
    with RECIPES_JSON.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("recipes.json must be a JSON array")
    return data


def _object_key_for_image(image_src: str) -> str:
    name = PurePosixPath(image_src).name or "dish.png"
    return f"recipes/seed_{name}"


async def _ensure_cover_file(
    file_repo: FileRepository,
    *,
    image_src: str,
    settings_bucket: str,
    public_base_url: str,
) -> uuid.UUID:
    """Create File meta with MinIO public URL (bytes uploaded by seed_minio_media)."""
    object_key = _object_key_for_image(image_src)
    public_url = f"{public_base_url.rstrip('/')}/{object_key}"
    existing = await file_repo.get_by_object_key(object_key)
    if existing is not None:
        existing.url = public_url
        existing.bucket = settings_bucket
        await file_repo.session.flush()
        return existing.id

    created = await file_repo.create(
        file_id=uuid.uuid4(),
        object_key=object_key,
        bucket=settings_bucket,
        original_filename=PurePosixPath(image_src).name or "dish.png",
        content_type="image/png" if image_src.endswith(".png") else "image/jpeg",
        size=0,
        category="recipes",
        url=public_url,
        etag=None,
    )
    return created.id


async def seed(session: AsyncSession) -> int:
    settings = get_settings()
    category_repo = CategoryRepository(session)
    file_repo = FileRepository(session)
    recipe_repo = RecipeRepository(session)
    recipes = load_recipes()
    count = 0

    for item in recipes:
        category = await category_repo.get_by_slug_any(item["category_slug"])
        if category is None:
            raise RuntimeError(
                f"Category '{item['category_slug']}' not found; "
                "run seed_categories.py first",
            )

        subcategory_id = None
        subcategory_slug = item.get("subcategory_slug")
        if subcategory_slug:
            subcategory = await category_repo.get_subcategory_by_slug(
                category_id=category.id,
                slug=subcategory_slug,
            )
            if subcategory is None:
                raise RuntimeError(
                    f"Subcategory '{subcategory_slug}' not found under "
                    f"'{item['category_slug']}'",
                )
            subcategory_id = subcategory.id

        cover_file_id = None
        image_src = item.get("image_src")
        if image_src:
            cover_file_id = await _ensure_cover_file(
                file_repo,
                image_src=image_src,
                settings_bucket=settings.storage_bucket,
                public_base_url=settings.storage_public_base_url,
            )

        created_at = None
        if item.get("created_at"):
            created_at = datetime.fromisoformat(
                item["created_at"].replace("Z", "+00:00"),
            )

        existing = await recipe_repo.get_by_title(item["title"])
        if existing is None:
            recipe = Recipe(
                title=item["title"],
                description=item.get("description") or "",
                category_id=category.id,
                subcategory_id=subcategory_id,
                cover_file_id=cover_file_id,
                likes=int(item.get("likes") or 0),
                recommends=item.get("recommends"),
                is_new=bool(item.get("is_new", False)),
                is_juicy=bool(item.get("is_juicy", False)),
                home_section=item.get("home_section"),
                display_category_slug=item.get("display_category_slug"),
            )
            if created_at is not None:
                recipe.created_at = created_at
                recipe.updated_at = created_at
            session.add(recipe)
        else:
            existing.description = item.get("description") or ""
            existing.category_id = category.id
            existing.subcategory_id = subcategory_id
            existing.cover_file_id = cover_file_id
            existing.likes = int(item.get("likes") or 0)
            existing.recommends = item.get("recommends")
            existing.is_new = bool(item.get("is_new", False))
            existing.is_juicy = bool(item.get("is_juicy", False))
            existing.home_section = item.get("home_section")
            existing.display_category_slug = item.get("display_category_slug")
            if created_at is not None:
                existing.created_at = created_at

        count += 1

    await session.commit()
    return count


async def main() -> None:
    async with AsyncSessionLocal() as session:
        total = await seed(session)
    print(f"Seeded {total} recipes (upsert by title).")


if __name__ == "__main__":
    asyncio.run(main())
