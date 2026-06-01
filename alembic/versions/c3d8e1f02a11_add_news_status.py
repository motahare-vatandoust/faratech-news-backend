"""add news status

Revision ID: c3d8e1f02a11
Revises: b2f4a8c91d03
Create Date: 2026-06-01

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c3d8e1f02a11"
down_revision: Union[str, None] = "b2f4a8c91d03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

news_status = sa.Enum("draft", "review", "published", name="news_status")


def upgrade() -> None:
    news_status.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "news",
        sa.Column(
            "status",
            news_status,
            nullable=False,
            server_default="published",
        ),
    )
    op.create_index("ix_news_status", "news", ["status"])
    op.alter_column("news", "status", server_default="draft")


def downgrade() -> None:
    op.drop_index("ix_news_status", table_name="news")
    op.drop_column("news", "status")
    news_status.drop(op.get_bind(), checkfirst=True)
