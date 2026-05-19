import socket
from datetime import datetime
from uuid import UUID

from celery.utils.log import get_task_logger

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.processing_job import ProcessingJob
from app.models.study import Study, StudyStatus
from app.services.audit import record_event
from app.services.storage import LocalStudyStorage
from processor_adapter import create_processor_adapter
from processor_adapter.artifacts import write_outputs_zip, write_technical_pdf
from worker.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(name="worker.tasks.process_study", bind=True, max_retries=0)
def process_study(self, study_id: str, job_id: str) -> None:
    settings = get_settings()
    storage = LocalStudyStorage(settings.storage_root)
    db = SessionLocal()
    study_uuid = UUID(study_id)
    job_uuid = UUID(job_id)

    try:
        study = db.get(Study, study_uuid)
        job = db.get(ProcessingJob, job_uuid)
        if not study or not job:
            logger.error("Study or job not found: %s %s", study_id, job_id)
            return

        now = datetime.utcnow()
        study.status = StudyStatus.processing
        study.processing_started_at = now
        study.error_message = None
        job.status = StudyStatus.processing.value
        job.started_at = now
        job.worker_name = socket.gethostname()
        record_event(db, "processing_started", study.id, {"job_id": str(job.id)})
        db.commit()

        processor_backend = study.processor_backend or settings.processor_backend
        adapter = create_processor_adapter(
            backend=processor_backend,
            processor_command=settings.processor_command,
            compneuro_command=settings.compneuro_command,
            compneuro_project_mount=settings.compneuro_project_mount,
            timeout_seconds=settings.processing_timeout_seconds,
        )

        result = adapter.run(
            input_dir=storage.input_dir(study.id),
            output_dir=storage.output_dir(study.id),
            study_id=str(study.id),
            logs_dir=storage.logs_dir(study.id),
            bids_project_dir=storage.bids_project_dir(study.id),
            runtime_project_dir=storage.runtime_project_dir(study.id),
        )

        finished = datetime.utcnow()
        job.finished_at = finished
        job.exit_code = result.exit_code
        job.log_path = str(result.log_path)
        study.processing_finished_at = finished
        study.output_path = str(storage.output_dir(study.id))
        study.preproc_output_path = str(result.preproc_path) if result.preproc_path else study.preproc_output_path

        if result.success:
            pdf_path = result.pdf_path
            output_zip_path = result.output_zip_path
            if processor_backend.strip().lower() == "compneuro":
                if settings.generate_output_zip and result.preproc_path:
                    output_zip_path = write_outputs_zip(result.preproc_path, storage.output_zip_path(study.id))
                    study.output_zip_path = str(output_zip_path)
                if settings.generate_technical_pdf:
                    pdf_path = write_technical_pdf(
                        storage.technical_report_path(study.id),
                        study_id=str(study.id),
                        bids_subject_id=study.bids_subject_id,
                        processor_name=study.processor_name,
                        processor_version=study.processor_version,
                        processor_backend=study.processor_backend,
                        status=StudyStatus.completed.value,
                        output_files=result.output_files,
                        warnings=result.warnings,
                    )
            study.status = StudyStatus.completed
            study.pdf_path = str(pdf_path) if pdf_path else None
            if output_zip_path:
                study.output_zip_path = str(output_zip_path)
            job.status = StudyStatus.completed.value
            record_event(
                db,
                "processing_completed",
                study.id,
                {
                    "pdf_path": str(pdf_path) if pdf_path else None,
                    "output_zip_path": str(output_zip_path) if output_zip_path else None,
                    "output_count": len(result.output_files),
                    "duration_seconds": result.duration_seconds,
                },
            )
        else:
            study.status = StudyStatus.failed
            study.error_message = result.error_message or "Error desconocido durante el procesamiento"
            job.status = StudyStatus.failed.value
            job.error_message = study.error_message
            record_event(db, "processing_failed", study.id, {"error": study.error_message, "exit_code": result.exit_code})

        db.commit()
    except Exception as exc:
        db.rollback()
        logger.exception("Unexpected worker error for study %s", study_id)
        study = db.get(Study, study_uuid)
        job = db.get(ProcessingJob, job_uuid)
        if study:
            study.status = StudyStatus.failed
            study.error_message = "Error interno durante el procesamiento"
            study.processing_finished_at = datetime.utcnow()
        if job:
            job.status = StudyStatus.failed.value
            job.finished_at = datetime.utcnow()
            job.error_message = str(exc)
        db.commit()
    finally:
        db.close()
