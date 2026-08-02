"""initial database schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS auth")
    op.execute("CREATE SCHEMA IF NOT EXISTS project")
    op.execute("CREATE SCHEMA IF NOT EXISTS germplasm")
    op.execute("CREATE SCHEMA IF NOT EXISTS phenotyping")
    op.execute("CREATE SCHEMA IF NOT EXISTS genomics")
    op.execute("CREATE SCHEMA IF NOT EXISTS molecular")
    op.execute("CREATE SCHEMA IF NOT EXISTS literature")
    op.execute("CREATE SCHEMA IF NOT EXISTS notebook")
    op.execute("CREATE SCHEMA IF NOT EXISTS lims")
    op.execute("CREATE SCHEMA IF NOT EXISTS reporting")
    op.execute("CREATE SCHEMA IF NOT EXISTS admin")

    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"pgcrypto\"")

    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("institution", sa.String(255), nullable=True),
        sa.Column("department", sa.String(255), nullable=True),
        sa.Column("role", sa.String(50), nullable=False, server_default="researcher"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("orcid_id", sa.String(50), nullable=True),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="auth",
    )

    op.create_table(
        "refresh_tokens",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="auth",
    )

    op.create_table(
        "audit_log",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("auth.users.id"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=True),
        sa.Column("resource_id", sa.String(255), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="admin",
    )


def downgrade() -> None:
    op.drop_table("audit_log", schema="admin")
    op.drop_table("refresh_tokens", schema="auth")
    op.drop_table("users", schema="auth")
    op.execute("DROP SCHEMA IF EXISTS admin")
    op.execute("DROP SCHEMA IF EXISTS reporting")
    op.execute("DROP SCHEMA IF EXISTS lims")
    op.execute("DROP SCHEMA IF EXISTS notebook")
    op.execute("DROP SCHEMA IF EXISTS literature")
    op.execute("DROP SCHEMA IF EXISTS molecular")
    op.execute("DROP SCHEMA IF EXISTS genomics")
    op.execute("DROP SCHEMA IF EXISTS phenotyping")
    op.execute("DROP SCHEMA IF EXISTS germplasm")
    op.execute("DROP SCHEMA IF EXISTS project")
    op.execute("DROP SCHEMA IF EXISTS auth")
