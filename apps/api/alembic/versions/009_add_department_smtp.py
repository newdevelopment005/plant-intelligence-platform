"""add department smtp settings

Revision ID: 009
Revises: 008
Create Date: 2026-08-14 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "departments",
        sa.Column("smtp_host", sa.String(length=255), nullable=True),
        schema="org",
    )
    op.add_column(
        "departments",
        sa.Column("smtp_port", sa.Integer(), nullable=True),
        schema="org",
    )
    op.add_column(
        "departments",
        sa.Column("smtp_user", sa.String(length=255), nullable=True),
        schema="org",
    )
    op.add_column(
        "departments",
        sa.Column("smtp_password", sa.String(length=255), nullable=True),
        schema="org",
    )
    op.add_column(
        "departments",
        sa.Column("smtp_from", sa.String(length=255), nullable=True),
        schema="org",
    )


def downgrade() -> None:
    op.drop_column("departments", "smtp_from", schema="org")
    op.drop_column("departments", "smtp_password", schema="org")
    op.drop_column("departments", "smtp_user", schema="org")
    op.drop_column("departments", "smtp_port", schema="org")
    op.drop_column("departments", "smtp_host", schema="org")
