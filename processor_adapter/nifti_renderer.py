from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class CommandRunner(Protocol):
    def __call__(self, args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]: ...


@dataclass(frozen=True)
class RenderedNifti:
    nifti_path: Path
    png_path: Path
    display_name: str
    success: bool
    error_message: str | None = None


def find_nifti_files(preproc_dir: Path, *, max_files: int = 50) -> list[Path]:
    if not preproc_dir.exists():
        return []
    candidates = sorted(path for path in preproc_dir.rglob("*") if path.is_file() and _is_nifti(path))
    return [path for path in candidates if not _is_temporary(path)][:max_files]


def build_slicer_command(renderer: str, nifti_path: Path, png_path: Path) -> list[str]:
    return [renderer, str(nifti_path), "-a", str(png_path)]


def render_nifti_outputs(
    preproc_dir: Path,
    rendered_png_dir: Path,
    *,
    renderer: str = "slicer",
    max_files: int = 50,
    timeout_seconds: int = 300,
    runner: CommandRunner | None = None,
    log_path: Path | None = None,
) -> list[RenderedNifti]:
    runner = runner or subprocess.run
    rendered_png_dir.mkdir(parents=True, exist_ok=True)
    artifacts: list[RenderedNifti] = []
    log_lines: list[str] = []

    for nifti_path in find_nifti_files(preproc_dir, max_files=max_files):
        display_name = _display_name(preproc_dir, nifti_path)
        png_path = rendered_png_dir / f"{_safe_png_stem(display_name)}.png"
        command = build_slicer_command(renderer, nifti_path, png_path)
        log_lines.append(f"COMMAND: {' '.join(command)}")
        try:
            completed = runner(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds or None,
            )
        except Exception as exc:  # pragma: no cover - defensive around external tools
            message = _public_error(exc)
            log_lines.append(f"ERROR: {message}")
            artifacts.append(RenderedNifti(nifti_path, png_path, display_name, False, message))
            continue

        if completed.returncode != 0:
            message = f"slicer terminó con código {completed.returncode}"
            log_lines.extend([f"EXIT_CODE: {completed.returncode}", f"STDERR: {completed.stderr}"])
            artifacts.append(RenderedNifti(nifti_path, png_path, display_name, False, message))
            continue
        if not png_path.exists():
            message = "slicer no generó el PNG esperado"
            log_lines.append(f"ERROR: {message}")
            artifacts.append(RenderedNifti(nifti_path, png_path, display_name, False, message))
            continue
        log_lines.append("EXIT_CODE: 0")
        artifacts.append(RenderedNifti(nifti_path, png_path, display_name, True))

    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        if not log_lines:
            log_lines.append(f"No se encontraron ficheros NIfTI en {preproc_dir}")
        log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    return artifacts


def _is_nifti(path: Path) -> bool:
    name = path.name.lower()
    return name.endswith(".nii") or name.endswith(".nii.gz")


def _is_temporary(path: Path) -> bool:
    lowered = path.name.lower()
    return lowered.startswith(".") or "tmp" in lowered or "temp" in lowered


def _display_name(preproc_dir: Path, nifti_path: Path) -> str:
    try:
        return nifti_path.relative_to(preproc_dir).as_posix()
    except ValueError:
        return nifti_path.name


def _safe_png_stem(display_name: str) -> str:
    stem = display_name
    if stem.lower().endswith(".nii.gz"):
        stem = stem[:-7]
    elif stem.lower().endswith(".nii"):
        stem = stem[:-4]
    return re.sub(r"[^A-Za-z0-9_.-]+", "__", stem).strip("._") or "output"


def _public_error(exc: Exception) -> str:
    if isinstance(exc, subprocess.TimeoutExpired):
        return "tiempo máximo de renderizado agotado"
    if isinstance(exc, FileNotFoundError):
        return "no se encontró la herramienta de renderizado"
    return "error renderizando NIfTI"
