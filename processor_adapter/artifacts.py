from __future__ import annotations

from datetime import datetime
from pathlib import Path

from processor_adapter.output_packager import list_output_files, write_outputs_zip
from processor_adapter.technical_pdf_report import TechnicalReportMetadata, write_technical_pdf_report


def write_technical_pdf(
    pdf_path: Path,
    *,
    study_id: str,
    bids_subject_id: str | None,
    processor_name: str | None,
    processor_version: str | None,
    processor_backend: str | None,
    status: str,
    output_files: list[Path],
    warnings: list[str] | None = None,
) -> Path:
    metadata = TechnicalReportMetadata(
        study_id=study_id,
        study_name=study_id,
        bids_subject_id=bids_subject_id,
        uploaded_at=None,
        processed_at=datetime.utcnow(),
        pipeline_name=processor_name,
        pipeline_version=processor_version,
        processor_backend=processor_backend,
        logical_output_path="output/Preproc",
    )
    return write_technical_pdf_report(
        pdf_path,
        metadata=metadata,
        rendered_outputs=[],
        output_files=output_files,
        warnings=[status, *(warnings or [])],
    )


__all__ = ["TechnicalReportMetadata", "list_output_files", "write_outputs_zip", "write_technical_pdf", "write_technical_pdf_report"]
