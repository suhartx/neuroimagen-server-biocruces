from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.study import ProcessingJobRead


class AdminQueueSummary(BaseModel):
    queued: int = 0
    processing: int = 0
    failed: int = 0
    active: int = 0
    worker_replicas: int = 0
    worker_concurrency: int = 0
    processing_capacity: int = 0
    processing_available: int = 0


class AdminUserSummary(BaseModel):
    total: int = 0
    active: int = 0
    admins: int = 0
    researchers: int = 0


class AdminStorageSummary(BaseModel):
    root: str
    exists: bool
    studies_bytes: int = 0
    disk_total_bytes: int = 0
    disk_used_bytes: int = 0
    disk_free_bytes: int = 0


class AdminServiceHealth(BaseModel):
    name: str
    status: str
    detail: str | None = None


class AdminDashboardRead(BaseModel):
    generated_at: datetime
    queue: AdminQueueSummary
    users: AdminUserSummary
    studies_by_status: dict[str, int] = Field(default_factory=dict)
    jobs_by_status: dict[str, int] = Field(default_factory=dict)
    storage: AdminStorageSummary
    services: list[AdminServiceHealth] = Field(default_factory=list)
    recent_failed_jobs: list[ProcessingJobRead] = Field(default_factory=list)
    alerts: list[str] = Field(default_factory=list)
