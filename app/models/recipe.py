from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.file import File
    from app.models.subcategory import SubCategory


class Recipe(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "recipes"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    subcategory_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subcategories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    cover_file_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("files.id", ondelete="SET NULL"),
        nullable=True,
    )
    likes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    recommends: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_new: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_juicy: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    home_section: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    display_category_slug: Mapped[str | None] = mapped_column(String(64), nullable=True)

    category: Mapped[Category] = relationship("Category", lazy="raise")
    subcategory: Mapped[SubCategory | None] = relationship("SubCategory", lazy="raise")
    cover_file: Mapped[File | None] = relationship("File", lazy="raise")
