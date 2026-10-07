"""create recipes table

Revision ID: 20261007203739
Revises: 20261007200449
Create Date: 2026-10-07 20:37:39.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20261007203739"
down_revision: Union[str, None] = "20261007200449"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "recipes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subcategory_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("cover_file_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("likes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("recommends", sa.Integer(), nullable=True),
        sa.Column("is_new", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_juicy", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("home_section", sa.String(length=32), nullable=True),
        sa.Column("display_category_slug", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["subcategory_id"],
            ["subcategories.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["cover_file_id"],
            ["files.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recipes_category_id"), "recipes", ["category_id"], unique=False)
    op.create_index(
        op.f("ix_recipes_subcategory_id"),
        "recipes",
        ["subcategory_id"],
        unique=False,
    )
    op.create_index(op.f("ix_recipes_is_juicy"), "recipes", ["is_juicy"], unique=False)
    op.create_index(op.f("ix_recipes_home_section"), "recipes", ["home_section"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_recipes_home_section"), table_name="recipes")
    op.drop_index(op.f("ix_recipes_is_juicy"), table_name="recipes")
    op.drop_index(op.f("ix_recipes_subcategory_id"), table_name="recipes")
    op.drop_index(op.f("ix_recipes_category_id"), table_name="recipes")
    op.drop_table("recipes")
