from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.models.processing_job import ProcessingJob
from app.models.study import Study, StudyStatus
from app.schemas.study import StudyRead, StudyStatusRead, UploadResponse
from app.services.audit import record_event
from app.services.security import validate_upload
from app.services.storage import LocalStudyStorage
from worker.tasks import process_study

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/studies/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
def upload_study(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> UploadResponse:
    safe_filename = validate_upload(file, settings.allowed_extension_list)
    study_id = uuid4()
    storage = LocalStudyStorage(settings.storage_root)

    stored_path, file_size, checksum = storage.save_upload(study_id, file, safe_filename)
    if file_size > settings.max_upload_size_bytes:
        storage.remove_study(study_id)
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="El fichero supera el tamaño máximo permitido")

    study = Study(
        id=study_id,
        original_filename=file.filename or safe_filename,
        stored_path=str(stored_path),
        output_path=str(storage.output_dir(study_id)),
        status=StudyStatus.queued,
        processor_name=settings.processor_name,
        processor_version=settings.processor_version,
        file_size=file_size,
        checksum=checksum,
    )
    job = ProcessingJob(study_id=study_id, status=StudyStatus.queued.value)
    db.add(study)
    db.add(job)
    record_event(db, "study_uploaded", study_id, {"filename": safe_filename}, ip_address=request.client.host if request.client else None)
    db.commit()

    storage.write_metadata(
        study_id,
        {
            "study_id": str(study_id),
            "original_filename": file.filename,
            "stored_filename": safe_filename,
            "checksum_sha256": checksum,
            "file_size": file_size,
        },
    )

    process_study.delay(str(study_id), str(job.id))
    return UploadResponse(id=study_id, status=study.status.value, message="Estudio recibido y encolado para procesamiento")


@router.get("/studies", response_model=list[StudyRead])
def list_studies(db: Session = Depends(get_db)) -> list[StudyRead]:
    studies = db.scalars(select(Study).order_by(Study.created_at.desc())).all()
    return [to_study_read(study) for study in studies]


@router.get("/studies/{study_id}", response_model=StudyRead)
def get_study(study_id: UUID, db: Session = Depends(get_db)) -> StudyRead:
    study = db.get(Study, study_id)
    if not study:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudio no encontrado")
    return to_study_read(study)


@router.get("/studies/{study_id}/status", response_model=StudyStatusRead)
def get_study_status(study_id: UUID, db: Session = Depends(get_db)) -> StudyStatusRead:
    study = db.get(Study, study_id)
    if not study:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudio no encontrado")
    return StudyStatusRead(
        id=study.id,
        status=study.status.value,
        error_message=study.error_message,
        has_pdf=bool(study.pdf_path),
        updated_at=study.updated_at,
    )


@router.get("/studies/{study_id}/download")
def download_pdf(study_id: UUID, db: Session = Depends(get_db)) -> FileResponse:
    study = db.get(Study, study_id)
    if not study:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudio no encontrado")
    if study.status != StudyStatus.completed or not study.pdf_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El informe PDF todavía no está disponible")
    pdf_path = Path(study.pdf_path)
    if not pdf_path.exists() or pdf_path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El informe PDF no existe en el almacenamiento")
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"informe-{study.id}.pdf")


def to_study_read(study: Study) -> StudyRead:
    return StudyRead(
        id=study.id,
        original_filename=study.original_filename,
        status=study.status.value,
        created_at=study.created_at,
        updated_at=study.updated_at,
        processing_started_at=study.processing_started_at,
        processing_finished_at=study.processing_finished_at,
        error_message=study.error_message,
        processor_name=study.processor_name,
        processor_version=study.processor_version,
        file_size=study.file_size,
        checksum=study.checksum,
        has_pdf=bool(study.pdf_path),
    )
