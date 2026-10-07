"""Upload local dish assets to MinIO and fix File.url to public MinIO links."""

from __future__ import annotations

import asyncio
import mimetypes
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.models.file import File
from app.storage.factory import StorageFactory

DISHES_DIR = BACKEND_ROOT.parent / "yee-daa" / "public" / "dishes"


def _content_type(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed or "application/octet-stream"


async def seed_media() -> None:
    if not DISHES_DIR.is_dir():
        raise FileNotFoundError(f"Dishes directory not found: {DISHES_DIR}")

    settings = get_settings()
    storage = StorageFactory.create(settings)
    files = sorted(p for p in DISHES_DIR.iterdir() if p.is_file())
    if not files:
        raise RuntimeError(f"No files in {DISHES_DIR}")

    uploaded: dict[str, tuple[str, int, str | None]] = {}

    for path in files:
        object_key = f"recipes/seed_{path.name}"
        data = path.read_bytes()
        content_type = _content_type(path)
        etag = await storage.upload(
            object_key=object_key,
            data=data,
            content_type=content_type,
        )
        public_url = storage.build_public_url(object_key)
        uploaded[object_key] = (public_url, len(data), etag)
        print(f"uploaded {object_key} -> {public_url} ({len(data)} bytes)")

    updated = 0
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(File))
        rows = list(result.scalars().all())
        for row in rows:
            payload = uploaded.get(row.object_key)
            if payload is None:
                # Also match by original filename under recipes/seed_*
                candidate = f"recipes/seed_{row.original_filename}"
                payload = uploaded.get(candidate)
                if payload is not None:
                    row.object_key = candidate
            if payload is None:
                continue
            public_url, size, etag = payload
            row.url = public_url
            row.size = size
            row.etag = etag
            row.bucket = settings.storage_bucket
            updated += 1
        await session.commit()

    print(f"Updated {updated} File rows with MinIO URLs.")


if __name__ == "__main__":
    asyncio.run(seed_media())
