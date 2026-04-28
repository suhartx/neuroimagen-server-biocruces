from pathlib import Path

from processor_adapter import ProcessorAdapter


def test_adapter_detects_generated_pdf(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"
    input_dir.mkdir()
    (input_dir / "study.nii").write_text("dummy", encoding="utf-8")
    script = Path("external_processor/dummy_processor.py").resolve()
    adapter = ProcessorAdapter(f"python {script} --input {{input_dir}} --output {{output_dir}} --study-id {{study_id}} --sleep 0")

    result = adapter.run(input_dir, output_dir, "abc", logs_dir)

    assert result.success is True
    assert result.exit_code == 0
    assert result.pdf_path is not None
    assert result.pdf_path.exists()
    assert result.log_path.exists()


def test_adapter_reports_failed_script(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"
    input_dir.mkdir()
    script = Path("external_processor/dummy_processor.py").resolve()
    adapter = ProcessorAdapter(f"python {script} --input {{input_dir}} --output {{output_dir}} --study-id {{study_id}} --sleep 0 --fail")

    result = adapter.run(input_dir, output_dir, "abc", logs_dir)

    assert result.success is False
    assert result.exit_code != 0
    assert result.error_message == "El procesador externo terminó con error"


def test_adapter_fails_without_pdf(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"
    input_dir.mkdir()
    adapter = ProcessorAdapter("python -c 'print(123)'")

    result = adapter.run(input_dir, output_dir, "abc", logs_dir)

    assert result.success is False
    assert result.error_message == "El procesador no generó ningún PDF"
