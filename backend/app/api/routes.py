from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.models.processing_job import ProcessingJob
from app.models.study import Study, StudyStatus
from app.schemas.study import StudyRead, StudyStatusRead, UploadResponse
from app.services.audit import record_event
from app.services.bids import prepare_single_subject_t1w_bids
from app.services.security import resolve_bids_subject_id, sanitize_filename, validate_nifti_gz_filename, validate_upload
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
    bids_subject_id: str | None = Form(None),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> UploadResponse:
    processor_backend = settings.processor_backend.strip().lower()
    if processor_backend == "compneuro":
        safe_filename = sanitize_filename(file.filename or "")
        validate_nifti_gz_filename(safe_filename)
    else:
        safe_filename = validate_upload(file, settings.allowed_extension_list)
    study_id = uuid4()
    resolved_bids_subject_id = resolve_bids_subject_id(bids_subject_id, study_id) if processor_backend == "compneuro" or bids_subject_id else None
    storage = LocalStudyStorage(settings.storage_root)

    stored_path, file_size, checksum = storage.save_upload(study_id, file, safe_filename)
    if file_size > settings.max_upload_size_bytes:
        storage.remove_study(study_id)
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="El fichero supera el tamaño máximo permitido")

    bids_paths = None
    if processor_backend == "compneuro" and resolved_bids_subject_id:
        try:
            bids_paths = prepare_single_subject_t1w_bids(storage, study_id, stored_path, resolved_bids_subject_id)
        except Exception as exc:
            storage.remove_study(study_id)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo preparar la estructura BIDS") from exc

    study = Study(
        id=study_id,
        original_filename=file.filename or safe_filename,
        stored_path=str(stored_path),
        output_path=str(storage.output_dir(study_id)),
        bids_path=str(bids_paths.bids_project_dir) if bids_paths else None,
        preproc_output_path=str(storage.preproc_output_dir(study_id)) if processor_backend == "compneuro" else None,
        bids_subject_id=resolved_bids_subject_id,
        processor_backend=processor_backend,
        container_image=settings.compneuro_container_image if processor_backend == "compneuro" else None,
        status=StudyStatus.queued,
        processor_name=settings.processor_name,
        processor_version=settings.processor_version,
        file_size=file_size,
        checksum=checksum,
    )
    job = ProcessingJob(study_id=study_id, status=StudyStatus.queued.value)
    db.add(study)
    db.add(job)
    record_event(
        db,
        "study_uploaded",
        study_id,
        {"filename": safe_filename, "processor_backend": processor_backend, "bids_subject_id": resolved_bids_subject_id},
        ip_address=request.client.host if request.client else None,
    )
    db.commit()

    storage.write_metadata(
        study_id,
        {
            "study_id": str(study_id),
            "original_filename": file.filename,
            "stored_filename": safe_filename,
            "checksum_sha256": checksum,
            "file_size": file_size,
            "processor_backend": processor_backend,
            "bids_subject_id": resolved_bids_subject_id,
            "bids_path": str(bids_paths.bids_project_dir) if bids_paths else None,
        },
    )

    process_study.delay(str(study_id), str(job.id))
    return UploadResponse(id=study_id, status=study.status.value, message="Estudio recibido y encolado para procesamiento", bids_subject_id=resolved_bids_subject_id)


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
        has_output_zip=bool(study.output_zip_path),
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
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"informe-tecnico-{study.id}.pdf")


@router.get("/studies/{study_id}/download/pdf")
def download_technical_pdf(study_id: UUID, db: Session = Depends(get_db)) -> FileResponse:
    return download_pdf(study_id, db)


@router.get("/studies/{study_id}/download/zip")
def download_outputs_zip(study_id: UUID, db: Session = Depends(get_db)) -> FileResponse:
    study = db.get(Study, study_id)
    if not study:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudio no encontrado")
    if study.status != StudyStatus.completed or not study.output_zip_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El ZIP de resultados todavía no está disponible")
    zip_path = Path(study.output_zip_path)
    if not zip_path.exists() or zip_path.suffix.lower() != ".zip":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El ZIP de resultados no existe en el almacenamiento")
    return FileResponse(zip_path, media_type="application/zip", filename=f"outputs-{study.id}.zip")


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
        processor_backend=study.processor_backend,
        bids_subject_id=study.bids_subject_id,
        file_size=study.file_size,
        checksum=study.checksum,
        has_pdf=bool(study.pdf_path),
        has_output_zip=bool(study.output_zip_path),
    )
