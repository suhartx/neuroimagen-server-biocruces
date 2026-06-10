from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NotificationRead(BaseModel):
    id: UUID
    recipient_user_id: UUID
    study_id: UUID | None = None
    event_type: str
    title: str
    message: str
    created_at: datetime
    read_at: datetime | None = None
    email_status: str
    email_sent_at: datetime | None = None

    model_config = {"from_attributes": True}
