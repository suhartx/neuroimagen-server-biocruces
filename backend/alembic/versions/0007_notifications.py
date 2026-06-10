"""notifications

Revision ID: 0007_notifications
Revises: 0006_share_links
Create Date: 2026-06-10
"""

from alembic import op
import sqlalchemy as sa

revision = "0007_notifications"
down_revision = "0006_share_links"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "notify_on_processing_completed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "notify_on_processing_failed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("recipient_user_id", sa.Uuid(), nullable=False),
        sa.Column("study_id", sa.Uuid()),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("read_at", sa.DateTime()),
        sa.Column("email_status", sa.String(length=50), nullable=False),
        sa.Column("email_sent_at", sa.DateTime()),
        sa.Column("email_error", sa.Text()),
        sa.ForeignKeyConstraint(["recipient_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["study_id"], ["studies.id"]),
    )
    op.create_index("ix_notifications_recipient_user_id", "notifications", ["recipient_user_id"])
    op.create_index("ix_notifications_study_id", "notifications", ["study_id"])
    op.create_index("ix_notifications_event_type", "notifications", ["event_type"])
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])
    op.alter_column("users", "notify_on_processing_completed", server_default=None)
    op.alter_column("users", "notify_on_processing_failed", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_notifications_created_at", table_name="notifications")
    op.drop_index("ix_notifications_event_type", table_name="notifications")
    op.drop_index("ix_notifications_study_id", table_name="notifications")
    op.drop_index("ix_notifications_recipient_user_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_column("users", "notify_on_processing_failed")
    op.drop_column("users", "notify_on_processing_completed")
