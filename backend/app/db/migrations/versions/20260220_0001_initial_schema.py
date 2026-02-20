"""Initial schema.

Revision ID: 20260220_0001
Revises:
Create Date: 2026-02-20 14:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260220_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("tier", sa.String(length=20), nullable=False, server_default="free"),
        sa.Column("grandma_mode", sa.Boolean(), nullable=True),
        sa.Column("language", sa.String(length=10), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)

    op.create_table(
        "scan_metadata",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("scan_type", sa.String(length=20), nullable=False),
        sa.Column("verdict", sa.String(length=20), nullable=False),
        sa.Column("confidence", sa.String(length=20), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("scam_pattern", sa.String(length=100), nullable=True),
        sa.Column("analysis_tier", sa.String(length=20), nullable=False, server_default="fast_path"),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scan_metadata_created_at"), "scan_metadata", ["created_at"], unique=False)
    op.create_index(op.f("ix_scan_metadata_user_id"), "scan_metadata", ["user_id"], unique=False)

    op.create_table(
        "url_cache",
        sa.Column("url_hash", sa.String(length=64), nullable=False),
        sa.Column("verdict", sa.String(length=20), nullable=False),
        sa.Column("confidence", sa.String(length=20), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("url_hash"),
    )

    op.create_table(
        "recovery_sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("steps_completed", sa.Integer(), nullable=True),
        sa.Column("total_steps", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recovery_sessions_user_id"), "recovery_sessions", ["user_id"], unique=False)

    op.create_table(
        "family_links",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("guardian_user_id", sa.String(length=36), nullable=False),
        sa.Column("member_user_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["guardian_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["member_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_family_links_guardian_user_id"), "family_links", ["guardian_user_id"], unique=False)
    op.create_index(op.f("ix_family_links_member_user_id"), "family_links", ["member_user_id"], unique=False)

    op.create_table(
        "feedback",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("scan_id", sa.String(length=36), nullable=False),
        sa.Column("user_reported_verdict", sa.String(length=50), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["scan_id"], ["scan_metadata.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_feedback_scan_id"), "feedback", ["scan_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_feedback_scan_id"), table_name="feedback")
    op.drop_table("feedback")
    op.drop_index(op.f("ix_family_links_member_user_id"), table_name="family_links")
    op.drop_index(op.f("ix_family_links_guardian_user_id"), table_name="family_links")
    op.drop_table("family_links")
    op.drop_index(op.f("ix_recovery_sessions_user_id"), table_name="recovery_sessions")
    op.drop_table("recovery_sessions")
    op.drop_table("url_cache")
    op.drop_index(op.f("ix_scan_metadata_user_id"), table_name="scan_metadata")
    op.drop_index(op.f("ix_scan_metadata_created_at"), table_name="scan_metadata")
    op.drop_table("scan_metadata")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
