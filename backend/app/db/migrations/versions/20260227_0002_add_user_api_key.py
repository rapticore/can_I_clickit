"""Add api_key column to users table.

Revision ID: 20260227_0002
Revises: 20260220_0001
Create Date: 2026-02-27 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260227_0002"
down_revision: Union[str, None] = "20260220_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("api_key", sa.String(length=64), nullable=True),
    )
    op.create_index(op.f("ix_users_api_key"), "users", ["api_key"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_api_key"), table_name="users")
    op.drop_column("users", "api_key")
