"""share links

Revision ID: 0006_share_links
Revises: 0005_job_management
Create Date: 2026-06-10
"""

from alembic import op
import sqlalchemy as sa

revision = "0006_share_links"
down_revision = "0005_job_management"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "share_links",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("study_id", sa.Uuid(), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_accessed_at", sa.DateTime()),
        sa.Column("access_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["study_id"], ["studies.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
    )
    op.create_index("ix_share_links_study_id", "share_links", ["study_id"])
    op.create_index(
        "ix_share_links_created_by_user_id", "share_links", ["created_by_user_id"]
    )
    op.create_index("ix_share_links_expires_at", "share_links", ["expires_at"])
    op.create_index(
        "ix_share_links_token_hash", "share_links", ["token_hash"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_share_links_token_hash", table_name="share_links")
    op.drop_index("ix_share_links_expires_at", table_name="share_links")
    op.drop_index("ix_share_links_created_by_user_id", table_name="share_links")
    op.drop_index("ix_share_links_study_id", table_name="share_links")
    op.drop_table("share_links")
