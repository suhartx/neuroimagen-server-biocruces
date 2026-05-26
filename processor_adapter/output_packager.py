from __future__ import annotations

import zipfile
from pathlib import Path


def list_output_files(preproc_dir: Path) -> list[Path]:
    if not preproc_dir.exists():
        return []
    return sorted(path for path in preproc_dir.rglob("*") if path.is_file())


def write_outputs_zip(output_dir: Path, zip_path: Path) -> Path:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in _zip_candidates(output_dir):
            archive.write(path, path.relative_to(output_dir))
    return zip_path


def _zip_candidates(output_dir: Path) -> list[Path]:
    if not output_dir.exists():
        return []
    return sorted(
        path
        for path in output_dir.rglob("*")
        if path.is_file()
        and path.name != "outputs.zip"
        and not path.name.startswith(".")
        and not _is_unnecessary_runtime_file(path)
    )


def _is_unnecessary_runtime_file(path: Path) -> bool:
    lowered = path.name.lower()
    return lowered.endswith(".log") or "tmp" in lowered or "temp" in lowered
