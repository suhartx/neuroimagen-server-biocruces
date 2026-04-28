import re
from pathlib import Path

from fastapi import HTTPException, UploadFile, status


def sanitize_filename(filename: str) -> str:
    name = Path(filename).name.strip().replace(" ", "_")
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    if not name or name in {".", ".."}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nombre de fichero no válido")
    return name[:255]


def has_allowed_extension(filename: str, allowed_extensions: list[str]) -> bool:
    lower_name = filename.lower()
    return any(lower_name.endswith(extension) for extension in allowed_extensions)


def validate_upload(upload: UploadFile, allowed_extensions: list[str]) -> str:
    safe_name = sanitize_filename(upload.filename or "")
    if not has_allowed_extension(safe_name, allowed_extensions):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Extensión de fichero no permitida")
    return safe_name
