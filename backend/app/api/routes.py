from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.models.processing_job import ProcessingJob
from app.models.study import Study, StudyStatus
from app.models.user import User, UserRole
from app.schemas.auth import (
    LoginRequest,
    LogoutResponse,
    TokenResponse,
    UserCreate,
    UserRead,
)
from app.schemas.study import StudyRead, StudyStatusRead, UploadResponse
from app.services.audit import record_event
from app.services.auth import (
    client_ip,
    create_access_token,
    get_current_user,
    get_user_by_email,
    hash_password,
    normalize_email,
    require_admin,
    require_study_access,
    verify_password,
)
from app.services.bids import prepare_single_subject_t1w_bids
from app.services.security import (
    resolve_bids_subject_id,
    sanitize_filename,
    validate_nifti_gz_filename,
    validate_upload,
)
from app.services.storage import LocalStudyStorage
from worker.tasks import process_study

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/auth/login", response_model=TokenResponse)
def login(
    request: Request,
    payload: LoginRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    user = get_user_by_email(db, payload.email)
    if (
        not user
        or not user.is_active
        or not verify_password(payload.password, user.hashed_password)
    ):
        record_event(
            db,
            "login_failed",
            details={"email": normalize_email(payload.email)},
            ip_address=client_ip(request),
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales no válidas"
        )

    user.last_login_at = datetime.utcnow()
    record_event(
        db,
        "login_succeeded",
        actor=user.email,
        actor_user_id=user.id,
        ip_address=client_ip(request),
    )
    db.commit()
    return TokenResponse(
        access_token=create_access_token(user, settings),
        user=UserRead.model_validate(user),
    )


@router.post("/auth/logout", response_model=LogoutResponse)
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LogoutResponse:
    record_event(
        db,
        "logout",
        actor=current_user.email,
        actor_user_id=current_user.id,
        ip_address=client_ip(request),
    )
    db.commit()
    return LogoutResponse(message="Sesión cerrada")


@router.get("/auth/me", response_model=UserRead)
def current_user(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)


@router.get("/users", response_model=list[UserRead])
def list_users(
    _: User = Depends(require_admin), db: Session = Depends(get_db)
) -> list[UserRead]:
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return [UserRead.model_validate(user) for user in users]


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserRead:
    if payload.role not in {UserRole.admin.value, UserRole.researcher.value}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Rol no válido"
        )
    user = User(
        email=normalize_email(payload.email),
        full_name=payload.full_name.strip(),
        hashed_password=hash_password(payload.password),
        role=payload.role,
        is_active=payload.is_active,
    )
    db.add(user)
    try:
        record_event(
            db,
            "user_created",
            actor=current_user.email,
            actor_user_id=current_user.id,
            details={"email": user.email, "role": user.role},
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese email",
        ) from None
    db.refresh(user)
    return UserRead.model_validate(user)


@router.post(
    "/studies/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_study(
    request: Request,
    file: UploadFile = File(...),
    bids_subject_id: str | None = Form(None),
    current_user: User = Depends(get_current_user),
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
    resolved_bids_subject_id = (
        resolve_bids_subject_id(bids_subject_id, study_id)
        if processor_backend == "compneuro" or bids_subject_id
        else None
    )
    storage = LocalStudyStorage(settings.storage_root)

    stored_path, file_size, checksum = storage.save_upload(
        study_id, file, safe_filename
    )
    if file_size > settings.max_upload_size_bytes:
        storage.remove_study(study_id)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="El fichero supera el tamaño máximo permitido",
        )

    bids_paths = None
    if processor_backend == "compneuro" and resolved_bids_subject_id:
        try:
            bids_paths = prepare_single_subject_t1w_bids(
                storage, study_id, stored_path, resolved_bids_subject_id
            )
        except Exception as exc:
            storage.remove_study(study_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo preparar la estructura BIDS",
            ) from exc

    study = Study(
        id=study_id,
        owner_user_id=current_user.id,
        original_filename=file.filename or safe_filename,
        stored_path=str(stored_path),
        output_path=str(storage.output_dir(study_id)),
        bids_path=str(bids_paths.bids_project_dir) if bids_paths else None,
        preproc_output_path=str(storage.preproc_output_dir(study_id))
        if processor_backend == "compneuro"
        else None,
        bids_subject_id=resolved_bids_subject_id,
        processor_backend=processor_backend,
        container_image=settings.compneuro_container_image
        if processor_backend == "compneuro"
        else None,
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
        {
            "filename": safe_filename,
            "processor_backend": processor_backend,
            "bids_subject_id": resolved_bids_subject_id,
        },
        actor=current_user.email,
        actor_user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )
    db.commit()

    storage.write_metadata(
        study_id,
        {
            "study_id": str(study_id),
            "owner_user_id": str(current_user.id),
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
    return UploadResponse(
        id=study_id,
        status=study.status.value,
        message="Estudio recibido y encolado para procesamiento",
        bids_subject_id=resolved_bids_subject_id,
    )


@router.get("/studies", response_model=list[StudyRead])
def list_studies(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[StudyRead]:
    query = select(Study).order_by(Study.created_at.desc())
    if current_user.role != UserRole.admin.value:
        query = query.where(Study.owner_user_id == current_user.id)
    studies = db.scalars(query).all()
    return [to_study_read(study) for study in studies]


@router.get("/studies/{study_id}", response_model=StudyRead)
def get_study(
    study_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudyRead:
    study = db.get(Study, study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Estudio no encontrado"
        )
    require_study_access(study.owner_user_id, current_user)
    return to_study_read(study)


@router.get("/studies/{study_id}/status", response_model=StudyStatusRead)
def get_study_status(
    study_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudyStatusRead:
    study = db.get(Study, study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Estudio no encontrado"
        )
    require_study_access(study.owner_user_id, current_user)
    return StudyStatusRead(
        id=study.id,
        status=study.status.value,
        error_message=study.error_message,
        has_pdf=bool(study.pdf_path),
        has_output_zip=bool(study.output_zip_path),
        processing_warnings=study.processing_warnings,
        updated_at=study.updated_at,
    )


@router.get("/studies/{study_id}/download")
def download_pdf(
    request: Request,
    study_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    study = db.get(Study, study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Estudio no encontrado"
        )
    require_study_access(study.owner_user_id, current_user)
    if study.status != StudyStatus.completed or not study.pdf_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El informe PDF todavía no está disponible",
        )
    pdf_path = Path(study.pdf_path)
    if not pdf_path.exists() or pdf_path.suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El informe PDF no existe en el almacenamiento",
        )
    record_event(
        db,
        "study_downloaded_pdf",
        study.id,
        actor=current_user.email,
        actor_user_id=current_user.id,
        ip_address=client_ip(request),
    )
    db.commit()
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"informe-tecnico-{study.id}.pdf",
    )


@router.get("/studies/{study_id}/download/pdf")
def download_technical_pdf(
    request: Request,
    study_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    return download_pdf(request, study_id, current_user, db)


@router.get("/studies/{study_id}/download/zip")
def download_outputs_zip(
    request: Request,
    study_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    study = db.get(Study, study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Estudio no encontrado"
        )
    require_study_access(study.owner_user_id, current_user)
    if study.status != StudyStatus.completed or not study.output_zip_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El ZIP de resultados todavía no está disponible",
        )
    zip_path = Path(study.output_zip_path)
    if not zip_path.exists() or zip_path.suffix.lower() != ".zip":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El ZIP de resultados no existe en el almacenamiento",
        )
    record_event(
        db,
        "study_downloaded_zip",
        study.id,
        actor=current_user.email,
        actor_user_id=current_user.id,
        ip_address=client_ip(request),
    )
    db.commit()
    return FileResponse(
        zip_path, media_type="application/zip", filename=f"outputs-{study.id}.zip"
    )


def to_study_read(study: Study) -> StudyRead:
    return StudyRead(
        id=study.id,
        owner_user_id=study.owner_user_id,
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
        processing_warnings=study.processing_warnings,
    )
