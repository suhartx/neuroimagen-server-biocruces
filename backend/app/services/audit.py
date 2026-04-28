import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent


def record_event(
    db: Session,
    event_type: str,
    study_id: UUID | None = None,
    details: dict | None = None,
    actor: str = "anonymous/system",
    ip_address: str | None = None,
) -> None:
    event = AuditEvent(
        study_id=study_id,
        event_type=event_type,
        details=json.dumps(details or {}, ensure_ascii=False),
        actor=actor,
        ip_address=ip_address,
    )
    db.add(event)
