import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProcessorResult:
    success: bool
    exit_code: int | None
    pdf_path: Path | None
    log_path: Path
    error_message: str | None
    duration_seconds: float


class ProcessorAdapter:
    """Adapter for an external CLI processor treated as a black box."""

    def __init__(self, command_template: str) -> None:
        self.command_template = command_template

    def run(self, input_dir: Path, output_dir: Path, study_id: str, logs_dir: Path) -> ProcessorResult:
        started = time.monotonic()
        input_dir = input_dir.resolve()
        output_dir = output_dir.resolve()
        logs_dir = logs_dir.resolve()
        log_path = logs_dir / "processor.log"

        if not input_dir.exists() or not input_dir.is_dir():
            logs_dir.mkdir(parents=True, exist_ok=True)
            log_path.write_text("Input directory does not exist\n", encoding="utf-8")
            return ProcessorResult(False, None, None, log_path, "No existe el directorio de entrada", 0.0)

        output_dir.mkdir(parents=True, exist_ok=True)
        logs_dir.mkdir(parents=True, exist_ok=True)

        command = self.command_template.format(
            input_dir=shlex.quote(str(input_dir)),
            output_dir=shlex.quote(str(output_dir)),
            study_id=shlex.quote(study_id),
            logs_dir=shlex.quote(str(logs_dir)),
        )

        try:
            completed = subprocess.run(
                command,
                shell=True,
                check=False,
                capture_output=True,
                text=True,
                timeout=None,
            )
        except Exception as exc:  # pragma: no cover - defensive around external tools
            duration = time.monotonic() - started
            log_path.write_text(f"COMMAND: {command}\nERROR: {exc}\n", encoding="utf-8")
            return ProcessorResult(False, None, None, log_path, "Error ejecutando el procesador externo", duration)

        duration = time.monotonic() - started
        log_path.write_text(
            "\n".join(
                [
                    f"COMMAND: {command}",
                    f"EXIT_CODE: {completed.returncode}",
                    "STDOUT:",
                    completed.stdout,
                    "STDERR:",
                    completed.stderr,
                ]
            ),
            encoding="utf-8",
        )

        if completed.returncode != 0:
            return ProcessorResult(False, completed.returncode, None, log_path, "El procesador externo terminó con error", duration)

        pdf_path = self._find_pdf(output_dir)
        if not pdf_path:
            return ProcessorResult(False, completed.returncode, None, log_path, "El procesador no generó ningún PDF", duration)

        return ProcessorResult(True, completed.returncode, pdf_path, log_path, None, duration)

    def _find_pdf(self, output_dir: Path) -> Path | None:
        pdfs = sorted(output_dir.rglob("*.pdf"))
        return pdfs[0] if pdfs else None
