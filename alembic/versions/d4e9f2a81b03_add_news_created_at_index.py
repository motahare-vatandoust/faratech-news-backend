"""add news created_at index

Revision ID: d4e9f2a81b03
Revises: f74d1d6527ce
Create Date: 2026-06-07

"""

from typing import Union

from alembic import op

revision: str = "d4e9f2a81b03"
down_revision: Union[str, None] = "f74d1d6527ce"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_news_created_at", "news", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_news_created_at", table_name="news")
