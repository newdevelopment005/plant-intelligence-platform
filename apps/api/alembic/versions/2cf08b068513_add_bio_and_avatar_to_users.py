"""add bio and avatar to users

Revision ID: 2cf08b068513
Revises: 002
Create Date: 2026-08-04 02:37:00.371064
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '2cf08b068513'
down_revision: str | None = '002'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("bio", sa.Text(), nullable=True), schema="auth")
    op.add_column("users", sa.Column("avatar_url", sa.String(500), nullable=True), schema="auth")


def downgrade() -> None:
    op.drop_column("users", "avatar_url", schema="auth")
    op.drop_column("users", "bio", schema="auth")
