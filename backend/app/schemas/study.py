from __future__ import annotations

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
    processor_backend: str | None = None
    bids_subject_id: str | None = None
    file_size: int | None = None
    checksum: str | None = None
    has_pdf: bool = False
    has_output_zip: bool = False
    processing_warnings: str | None = None

    model_config = {"from_attributes": True}


class StudyStatusRead(BaseModel):
    id: UUID
    status: str
    error_message: str | None = None
    has_pdf: bool
    has_output_zip: bool = False
    processing_warnings: str | None = None
    updated_at: datetime


class UploadResponse(BaseModel):
    id: UUID
    status: str
    message: str
    bids_subject_id: str | None = None
