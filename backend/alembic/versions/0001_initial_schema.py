"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-04-28
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    status_enum = postgresql.ENUM(
        "uploaded",
        "queued",
        "processing",
        "completed",
        "failed",
        name="studystatus",
        create_type=False,
    )
    status_enum.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "studies",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("original_filename", sa.String(length=512), nullable=False),
        sa.Column("stored_path", sa.Text(), nullable=False),
        sa.Column("output_path", sa.Text()),
        sa.Column("pdf_path", sa.Text()),
        sa.Column("status", status_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("processing_started_at", sa.DateTime()),
        sa.Column("processing_finished_at", sa.DateTime()),
        sa.Column("error_message", sa.Text()),
        sa.Column("processor_name", sa.String(length=255)),
        sa.Column("processor_version", sa.String(length=100)),
        sa.Column("file_size", sa.BigInteger()),
        sa.Column("checksum", sa.String(length=128)),
    )
    op.create_table(
        "processing_jobs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("study_id", sa.Uuid(), sa.ForeignKey("studies.id"), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("queued_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime()),
        sa.Column("finished_at", sa.DateTime()),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("worker_name", sa.String(length=255)),
        sa.Column("exit_code", sa.Integer()),
        sa.Column("log_path", sa.Text()),
        sa.Column("error_message", sa.Text()),
    )
    op.create_index("ix_processing_jobs_study_id", "processing_jobs", ["study_id"])
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("study_id", sa.Uuid(), sa.ForeignKey("studies.id")),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("details", sa.Text()),
        sa.Column("actor", sa.String(length=255), nullable=False),
        sa.Column("ip_address", sa.String(length=64)),
    )
    op.create_index("ix_audit_events_study_id", "audit_events", ["study_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_events_study_id", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_index("ix_processing_jobs_study_id", table_name="processing_jobs")
    op.drop_table("processing_jobs")
    op.drop_table("studies")
    sa.Enum(name="studystatus").drop(op.get_bind(), checkfirst=True)
