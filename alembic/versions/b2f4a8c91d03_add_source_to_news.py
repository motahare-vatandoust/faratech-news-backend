"""add source to news

Revision ID: b2f4a8c91d03
Revises: aec833277511
Create Date: 2026-05-31 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b2f4a8c91d03"
down_revision: Union[str, Sequence[str], None] = "aec833277511"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("news", sa.Column("source", sa.String(length=64), nullable=True))
    op.create_index("ix_news_source", "news", ["source"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_news_source", table_name="news")
    op.drop_column("news", "source")
