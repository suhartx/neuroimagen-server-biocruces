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
from processor_adapter import ProcessorAdapter
from worker.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(name="worker.tasks.process_study", bind=True, max_retries=0)
def process_study(self, study_id: str, job_id: str) -> None:
    settings = get_settings()
    storage = LocalStudyStorage(settings.storage_root)
    adapter = ProcessorAdapter(settings.processor_command)
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

        result = adapter.run(
            input_dir=storage.input_dir(study.id),
            output_dir=storage.output_dir(study.id),
            study_id=str(study.id),
            logs_dir=storage.logs_dir(study.id),
        )

        finished = datetime.utcnow()
        job.finished_at = finished
        job.exit_code = result.exit_code
        job.log_path = str(result.log_path)
        study.processing_finished_at = finished
        study.output_path = str(storage.output_dir(study.id))

        if result.success and result.pdf_path:
            study.status = StudyStatus.completed
            study.pdf_path = str(result.pdf_path)
            job.status = StudyStatus.completed.value
            record_event(db, "processing_completed", study.id, {"pdf_path": str(result.pdf_path), "duration_seconds": result.duration_seconds})
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
