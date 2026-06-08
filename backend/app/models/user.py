from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


SYSTEM_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


class UserRole(str, enum.Enum):
    admin = "admin"
    researcher = "researcher"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(Text)
    role: Mapped[str] = mapped_column(
        String(50), default=UserRole.researcher.value, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)

    studies = relationship("Study", back_populates="owner")
    audit_events = relationship("AuditEvent", back_populates="actor_user")

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.admin.value
