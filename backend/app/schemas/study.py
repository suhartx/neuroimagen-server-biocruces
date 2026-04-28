from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class StudyRead(BaseModel):
    id: UUID
    original_filename: str
    status: str
    created_at: datetime
    updated_at: datetime
    processing_started_at: datetime | None = None
    processing_finished_at: datetime | None = None
    error_message: str | None = None
    processor_name: str | None = None
    processor_version: str | None = None
    file_size: int | None = None
    checksum: str | None = None
    has_pdf: bool = False

    model_config = {"from_attributes": True}


class StudyStatusRead(BaseModel):
    id: UUID
    status: str
    error_message: str | None = None
    has_pdf: bool
    updated_at: datetime


class UploadResponse(BaseModel):
    id: UUID
    status: str
    message: str
