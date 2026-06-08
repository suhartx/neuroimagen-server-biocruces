"""multiuser auth

Revision ID: 0004_multiuser_auth
Revises: 0003_rendered_outputs_metadata
Create Date: 2026-06-05
"""

import uuid
from datetime import datetime

from alembic import op
import sqlalchemy as sa

revision = "0004_multiuser_auth"
down_revision = "0003_rendered_outputs_metadata"
branch_labels = None
depends_on = None

SYSTEM_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.Text()),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("last_login_at", sa.DateTime()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    users_table = sa.table(
        "users",
        sa.column("id", sa.Uuid()),
        sa.column("email", sa.String()),
        sa.column("full_name", sa.String()),
        sa.column("hashed_password", sa.Text()),
        sa.column("role", sa.String()),
        sa.column("is_active", sa.Boolean()),
        sa.column("created_at", sa.DateTime()),
        sa.column("updated_at", sa.DateTime()),
    )
    now = datetime.utcnow()
    op.bulk_insert(
        users_table,
        [
            {
                "id": SYSTEM_USER_ID,
                "email": "system@local",
                "full_name": "System user",
                "hashed_password": None,
                "role": "admin",
                "is_active": False,
                "created_at": now,
                "updated_at": now,
            }
        ],
    )

    op.add_column("studies", sa.Column("owner_user_id", sa.Uuid(), nullable=True))
    op.create_index("ix_studies_owner_user_id", "studies", ["owner_user_id"])
    op.create_foreign_key(
        "fk_studies_owner_user_id_users", "studies", "users", ["owner_user_id"], ["id"]
    )
    op.execute(
        sa.text(
            "UPDATE studies SET owner_user_id = :system_user_id WHERE owner_user_id IS NULL"
        ).bindparams(
            sa.bindparam("system_user_id", value=SYSTEM_USER_ID, type_=sa.Uuid())
        )
    )
    op.alter_column("studies", "owner_user_id", nullable=False)

    op.add_column("audit_events", sa.Column("actor_user_id", sa.Uuid(), nullable=True))
    op.create_index("ix_audit_events_actor_user_id", "audit_events", ["actor_user_id"])
    op.create_foreign_key(
        "fk_audit_events_actor_user_id_users",
        "audit_events",
        "users",
        ["actor_user_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_audit_events_actor_user_id_users", "audit_events", type_="foreignkey"
    )
    op.drop_index("ix_audit_events_actor_user_id", table_name="audit_events")
    op.drop_column("audit_events", "actor_user_id")

    op.drop_constraint("fk_studies_owner_user_id_users", "studies", type_="foreignkey")
    op.drop_index("ix_studies_owner_user_id", table_name="studies")
    op.drop_column("studies", "owner_user_id")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
