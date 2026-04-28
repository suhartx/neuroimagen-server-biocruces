import hashlib
import json
import shutil
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile


class LocalStudyStorage:
    def __init__(self, root: Path) -> None:
        self.root = root

    def study_dir(self, study_id: UUID) -> Path:
        return self.root / str(study_id)

    def input_dir(self, study_id: UUID) -> Path:
        return self.study_dir(study_id) / "input"

    def output_dir(self, study_id: UUID) -> Path:
        return self.study_dir(study_id) / "output"

    def logs_dir(self, study_id: UUID) -> Path:
        return self.study_dir(study_id) / "logs"

    def prepare(self, study_id: UUID) -> None:
        for directory in [self.input_dir(study_id), self.output_dir(study_id), self.logs_dir(study_id)]:
            directory.mkdir(parents=True, exist_ok=True)

    def safe_path(self, base: Path, filename: str) -> Path:
        target = (base / filename).resolve()
        if base.resolve() not in target.parents and target != base.resolve():
            raise ValueError("Ruta de fichero no permitida")
        return target

    def save_upload(self, study_id: UUID, upload: UploadFile, safe_filename: str) -> tuple[Path, int, str]:
        self.prepare(study_id)
        destination = self.safe_path(self.input_dir(study_id), safe_filename)
        hasher = hashlib.sha256()
        size = 0
        with destination.open("wb") as out_file:
            while chunk := upload.file.read(1024 * 1024):
                size += len(chunk)
                hasher.update(chunk)
                out_file.write(chunk)
        return destination, size, hasher.hexdigest()

    def write_metadata(self, study_id: UUID, metadata: dict) -> None:
        path = self.study_dir(study_id) / "metadata.json"
        path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    def remove_study(self, study_id: UUID) -> None:
        shutil.rmtree(self.study_dir(study_id), ignore_errors=True)
