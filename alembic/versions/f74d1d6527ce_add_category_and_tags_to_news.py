"""add category and tags to news

Revision ID: f74d1d6527ce
Revises: ea1a7c44b9f2
Create Date: 2026-06-02

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f74d1d6527ce"
down_revision: Union[str, None] = "ea1a7c44b9f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("news", sa.Column("category", sa.String(length=128), nullable=True))
    op.add_column("news", sa.Column("tags", sa.JSON(), nullable=True))
    op.create_index("ix_news_category", "news", ["category"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_news_category", table_name="news")
    op.drop_column("news", "tags")
    op.drop_column("news", "category")
