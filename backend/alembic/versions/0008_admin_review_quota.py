"""admin review quota

Revision ID: 0008_admin_review_quota
Revises: 0007_notifications
Create Date: 2026-07-02
"""

from alembic import op
import sqlalchemy as sa

revision = "0008_admin_review_quota"
down_revision = "0007_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("deleted_at", sa.DateTime()))
    op.add_column("users", sa.Column("storage_quota_bytes", sa.BigInteger()))
    op.add_column(
        "studies",
        sa.Column(
            "clinical_review_status",
            sa.String(length=50),
            nullable=False,
            server_default="technical_only",
        ),
    )
    op.alter_column("studies", "clinical_review_status", server_default=None)


def downgrade() -> None:
    op.drop_column("studies", "clinical_review_status")
    op.drop_column("users", "storage_quota_bytes")
    op.drop_column("users", "deleted_at")
