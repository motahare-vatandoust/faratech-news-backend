"""add cover_image_url to news

Revision ID: e5a1b2c3d4f5
Revises: d4e9f2a81b03
Create Date: 2026-07-20

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e5a1b2c3d4f5"
down_revision: Union[str, None] = "d4e9f2a81b03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "news",
        sa.Column("cover_image_url", sa.String(length=2048), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("news", "cover_image_url")
