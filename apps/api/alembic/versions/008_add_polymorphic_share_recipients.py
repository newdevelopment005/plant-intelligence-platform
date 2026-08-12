"""polymorphic share recipients: team and department targets

Revision ID: 008
Revises: 007
Create Date: 2026-08-12 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "share_recipients",
        sa.Column("recipient_type", sa.String(length=20), nullable=False, server_default="user"),
        schema="sharing",
    )
    op.alter_column(
        "share_recipients",
        "user_id",
        existing_type=UUID(as_uuid=True),
        nullable=True,
        schema="sharing",
    )
    op.add_column(
        "share_recipients",
        sa.Column(
            "team_id",
            UUID(as_uuid=True),
            sa.ForeignKey("team.teams.id", ondelete="CASCADE"),
            nullable=True,
        ),
        schema="sharing",
    )
    op.add_column(
        "share_recipients",
        sa.Column(
            "department_id",
            UUID(as_uuid=True),
            sa.ForeignKey("org.departments.id", ondelete="CASCADE"),
            nullable=True,
        ),
        schema="sharing",
    )
    op.create_index(
        "ix_sharing_share_recipients_team_id",
        "share_recipients",
        ["team_id"],
        schema="sharing",
    )
    op.create_index(
        "ix_sharing_share_recipients_department_id",
        "share_recipients",
        ["department_id"],
        schema="sharing",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_sharing_share_recipients_department_id",
        table_name="share_recipients",
        schema="sharing",
    )
    op.drop_index(
        "ix_sharing_share_recipients_team_id",
        table_name="share_recipients",
        schema="sharing",
    )
    op.drop_column("share_recipients", "department_id", schema="sharing")
    op.drop_column("share_recipients", "team_id", schema="sharing")
    op.alter_column(
        "share_recipients",
        "user_id",
        existing_type=UUID(as_uuid=True),
        nullable=False,
        schema="sharing",
    )
    op.drop_column("share_recipients", "recipient_type", schema="sharing")
