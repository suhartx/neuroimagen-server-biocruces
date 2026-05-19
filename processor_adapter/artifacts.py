from __future__ import annotations

import html
import textwrap
import zipfile
from datetime import datetime
from pathlib import Path


def list_output_files(preproc_dir: Path) -> list[Path]:
    if not preproc_dir.exists():
        return []
    return sorted(path for path in preproc_dir.rglob("*") if path.is_file())


def write_outputs_zip(preproc_dir: Path, zip_path: Path) -> Path:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in list_output_files(preproc_dir):
            archive.write(path, path.relative_to(preproc_dir.parent))
    return zip_path


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
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "Resumen tecnico de procesamiento",
        "No es un informe clinico.",
        f"Study ID: {study_id}",
        f"Subject BIDS: {bids_subject_id or 'n/a'}",
        f"Generated at UTC: {datetime.utcnow().isoformat(timespec='seconds')}",
        f"Status: {status}",
        f"Processor backend: {processor_backend or 'n/a'}",
        f"Processor: {processor_name or 'n/a'}",
        f"Processor version: {processor_version or 'n/a'}",
        "Outputs:",
    ]
    lines.extend(f"- {path.as_posix()}" for path in output_files[:120])
    if len(output_files) > 120:
        lines.append(f"- ... {len(output_files) - 120} more files")
    if warnings:
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in warnings)

    _write_simple_pdf(pdf_path, lines)
    return pdf_path


def _write_simple_pdf(path: Path, lines: list[str]) -> None:
    content_lines = []
    y = 800
    for line in lines:
        for wrapped in textwrap.wrap(line, width=92) or [""]:
            safe = _pdf_text(wrapped)
            content_lines.append(f"BT /F1 9 Tf 40 {y} Td ({safe}) Tj ET")
            y -= 13
            if y < 40:
                break
        if y < 40:
            break
    stream = "\n".join(content_lines)
    objects = [
        "1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj",
        "2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj",
        "3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 595 842]/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj",
        "4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj",
        f"5 0 obj<</Length {len(stream.encode('latin-1', errors='replace'))}>>stream\n{stream}\nendstream endobj",
    ]
    pdf = "%PDF-1.4\n" + "\n".join(objects) + "\ntrailer<</Root 1 0 R>>\n%%EOF\n"
    path.write_bytes(pdf.encode("latin-1", errors="replace"))


def _pdf_text(value: str) -> str:
    escaped = html.unescape(value).encode("latin-1", errors="replace").decode("latin-1")
    return escaped.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
