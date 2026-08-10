"""change shares.item_id column to string

Revision ID: 005
Revises: 004
Create Date: 2026-08-10 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "shares",
        "item_id",
        existing_type=sa.dialects.postgresql.UUID(as_uuid=True),
        type_=sa.String(255),
        existing_nullable=False,
        schema="sharing",
    )


def downgrade() -> None:
    op.alter_column(
        "shares",
        "item_id",
        existing_type=sa.String(255),
        type_=sa.dialects.postgresql.UUID(as_uuid=True),
        existing_nullable=False,
        schema="sharing",
    )