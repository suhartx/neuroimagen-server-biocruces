"""rendered outputs metadata

Revision ID: 0003_rendered_outputs_metadata
Revises: 0002_compneuro_integration
Create Date: 2026-05-25
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_rendered_outputs_metadata"
down_revision = "0002_compneuro_integration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("studies", sa.Column("rendered_png_dir", sa.Text()))
    op.add_column("studies", sa.Column("processing_warnings", sa.Text()))


def downgrade() -> None:
    op.drop_column("studies", "processing_warnings")
    op.drop_column("studies", "rendered_png_dir")
