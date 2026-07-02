from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UserRead(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    deleted_at: datetime | None = None
    storage_quota_bytes: int | None = None
    storage_used_bytes: int = 0
    notify_on_processing_completed: bool
    notify_on_processing_failed: bool

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class UserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=256)
    role: str = "researcher"
    is_active: bool = True
    storage_quota_bytes: int | None = Field(default=None, ge=0)


class UserUpdate(BaseModel):
    is_active: bool | None = None
    storage_quota_bytes: int | None = Field(default=None, ge=0)


class UserActionResponse(BaseModel):
    id: UUID
    message: str


class NotificationPreferences(BaseModel):
    notify_on_processing_completed: bool
    notify_on_processing_failed: bool


class LogoutResponse(BaseModel):
    message: str
