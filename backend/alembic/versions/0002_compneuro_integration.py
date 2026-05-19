"""compneuro integration metadata

Revision ID: 0002_compneuro_integration
Revises: 0001_initial_schema
Create Date: 2026-05-19
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_compneuro_integration"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("studies", sa.Column("output_zip_path", sa.Text()))
    op.add_column("studies", sa.Column("bids_subject_id", sa.String(length=128)))
    op.add_column("studies", sa.Column("processor_backend", sa.String(length=100)))
    op.add_column("studies", sa.Column("container_image", sa.String(length=255)))
    op.add_column("studies", sa.Column("bids_path", sa.Text()))
    op.add_column("studies", sa.Column("preproc_output_path", sa.Text()))


def downgrade() -> None:
    op.drop_column("studies", "preproc_output_path")
    op.drop_column("studies", "bids_path")
    op.drop_column("studies", "container_image")
    op.drop_column("studies", "processor_backend")
    op.drop_column("studies", "bids_subject_id")
    op.drop_column("studies", "output_zip_path")
