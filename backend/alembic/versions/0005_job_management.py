"""job management

Revision ID: 0005_job_management
Revises: 0004_multiuser_auth
Create Date: 2026-06-05
"""

from alembic import op
import sqlalchemy as sa

revision = "0005_job_management"
down_revision = "0004_multiuser_auth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE studystatus ADD VALUE IF NOT EXISTS 'canceled'")
    op.add_column("studies", sa.Column("deleted_at", sa.DateTime()))
    op.add_column("processing_jobs", sa.Column("celery_task_id", sa.String(length=255)))
    op.create_index(
        "ix_processing_jobs_celery_task_id", "processing_jobs", ["celery_task_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_processing_jobs_celery_task_id", table_name="processing_jobs")
    op.drop_column("processing_jobs", "celery_task_id")
    op.drop_column("studies", "deleted_at")
