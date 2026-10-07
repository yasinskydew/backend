"""Idempotent upsert of categories from scripts/data/categories.json."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

# Ensure backend root is on sys.path when run as a script
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.repositories.category_repository import CategoryRepository

CATEGORIES_JSON = Path(__file__).resolve().parent / "data" / "categories.json"


def load_categories() -> list[dict]:
    if not CATEGORIES_JSON.exists():
        raise FileNotFoundError(f"Categories JSON not found: {CATEGORIES_JSON}")
    with CATEGORIES_JSON.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("categories.json must be a JSON array")
    return data


async def seed(session: AsyncSession) -> tuple[int, int]:
    repo = CategoryRepository(session)
    categories = load_categories()
    category_count = 0
    subcategory_count = 0

    for cat_index, item in enumerate(categories):
        category = await repo.upsert_category(
            slug=item["slug"],
            title=item["title"],
            icon=item["icon"],
            sort_order=cat_index,
            is_active=True,
        )
        category_count += 1

        children = item.get("children") or []
        for child_index, child in enumerate(children):
            await repo.upsert_subcategory(
                category_id=category.id,
                slug=child["slug"],
                title=child["title"],
                sort_order=child_index,
                is_active=True,
            )
            subcategory_count += 1

    await session.commit()
    return category_count, subcategory_count


async def main() -> None:
    async with AsyncSessionLocal() as session:
        cat_count, sub_count = await seed(session)
    print(f"Seeded {cat_count} categories and {sub_count} subcategories (upsert).")


if __name__ == "__main__":
    asyncio.run(main())
