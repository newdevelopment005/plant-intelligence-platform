"""add org hierarchy: users.department_id and team department/parent links

Revision ID: 007
Revises: 006
Create Date: 2026-08-12 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "department_id",
            UUID(as_uuid=True),
            sa.ForeignKey("org.departments.id", ondelete="SET NULL"),
            nullable=True,
        ),
        schema="auth",
    )
    op.create_index("ix_auth_users_department_id", "users", ["department_id"], schema="auth")

    op.add_column(
        "teams",
        sa.Column(
            "department_id",
            UUID(as_uuid=True),
            sa.ForeignKey("org.departments.id", ondelete="SET NULL"),
            nullable=True,
        ),
        schema="team",
    )
    op.create_index("ix_team_teams_department_id", "teams", ["department_id"], schema="team")

    op.add_column(
        "teams",
        sa.Column(
            "parent_id",
            UUID(as_uuid=True),
            sa.ForeignKey("team.teams.id", ondelete="CASCADE"),
            nullable=True,
        ),
        schema="team",
    )
    op.create_index("ix_team_teams_parent_id", "teams", ["parent_id"], schema="team")


def downgrade() -> None:
    op.drop_index("ix_team_teams_parent_id", table_name="teams", schema="team")
    op.drop_column("teams", "parent_id", schema="team")
    op.drop_index("ix_team_teams_department_id", table_name="teams", schema="team")
    op.drop_column("teams", "department_id", schema="team")
    op.drop_index("ix_auth_users_department_id", table_name="users", schema="auth")
    op.drop_column("users", "department_id", schema="auth")
