"""add sharing and teams tables

Revision ID: 003
Revises: 002
Create Date: 2026-08-05 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "003"
down_revision: Union[str, None] = ("002", "2cf08b068513")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS sharing")
    op.execute("CREATE SCHEMA IF NOT EXISTS team")

    # =============================================
    # SHARING MODULE
    # =============================================
    op.create_table(
        "shares",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("item_type", sa.String(50), nullable=False),
        sa.Column("item_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("owner_id", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("visibility", sa.String(20), nullable=False, server_default="private"),
        sa.Column("share_token", sa.String(100), nullable=True, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="sharing",
    )

    op.create_table(
        "share_recipients",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("share_id", UUID(as_uuid=True), sa.ForeignKey("sharing.shares.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("permission", sa.String(20), nullable=False, server_default="read"),
        sa.Column("shared_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="sharing",
    )

    # =============================================
    # TEAM MODULE
    # =============================================
    op.create_table(
        "teams",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("owner_id", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="team",
    )

    op.create_table(
        "team_members",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("team_id", UUID(as_uuid=True), sa.ForeignKey("team.teams.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("role", sa.String(50), nullable=False, server_default="member"),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="team",
    )


def downgrade() -> None:
    op.drop_table("share_recipients", schema="sharing")
    op.drop_table("shares", schema="sharing")
    op.drop_table("team_members", schema="team")
    op.drop_table("teams", schema="team")
    op.execute("DROP SCHEMA IF EXISTS sharing")
    op.execute("DROP SCHEMA IF EXISTS team")
