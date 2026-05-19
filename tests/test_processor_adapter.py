from pathlib import Path

from processor_adapter import CompneuroAnatprocAdapter, ProcessorAdapter
from processor_adapter.artifacts import write_outputs_zip, write_technical_pdf


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


def test_compneuro_adapter_detects_preproc_outputs(tmp_path):
    bids_project_dir = tmp_path / "bids_project"
    data_dir = bids_project_dir / "data"
    anat_dir = data_dir / "sub-O01" / "anat"
    anat_dir.mkdir(parents=True)
    (anat_dir / "sub-O01_T1w.nii.gz").write_bytes(b"nifti")
    (data_dir / "participants.tsv").write_text("participant_id\nsub-O01\n", encoding="utf-8")
    output_dir = tmp_path / "output"
    logs_dir = tmp_path / "logs"
    runtime_project_dir = tmp_path / "runtime_project"
    project_mount = tmp_path / "project"
    adapter = CompneuroAnatprocAdapter(
        "mkdir -p {project_dir}/Preproc/BET {project_dir}/Preproc/ProbTissue && "
        "touch {project_dir}/Preproc/BET/sub-O01_T1w_brain.nii.gz "
        "{project_dir}/Preproc/ProbTissue/sub-O01_T1w_brain_CSF.nii.gz",
        project_mount=project_mount,
    )

    result = adapter.run(
        input_dir=tmp_path / "input",
        output_dir=output_dir,
        study_id="abc",
        logs_dir=logs_dir,
        bids_project_dir=bids_project_dir,
        runtime_project_dir=runtime_project_dir,
    )

    assert result.success is True
    assert result.exit_code == 0
    assert (output_dir / "Preproc" / "BET").is_dir()
    assert (output_dir / "Preproc" / "ProbTissue").is_dir()
    assert len(result.output_files) == 2


def test_compneuro_adapter_fails_if_project_mount_is_not_managed(tmp_path):
    bids_project_dir = tmp_path / "bids_project"
    (bids_project_dir / "data").mkdir(parents=True)
    logs_dir = tmp_path / "logs"
    project_mount = tmp_path / "project"
    project_mount.mkdir()
    adapter = CompneuroAnatprocAdapter("true", project_mount=project_mount)

    result = adapter.run(
        input_dir=tmp_path / "input",
        output_dir=tmp_path / "output",
        study_id="abc",
        logs_dir=logs_dir,
        bids_project_dir=bids_project_dir,
        runtime_project_dir=tmp_path / "runtime_project",
    )

    assert result.success is False
    assert result.error_message == "No se pudo preparar el entorno /project"


def test_technical_pdf_and_zip_are_generated(tmp_path):
    preproc_dir = tmp_path / "Preproc"
    (preproc_dir / "BET").mkdir(parents=True)
    (preproc_dir / "ProbTissue").mkdir()
    output_file = preproc_dir / "BET" / "sub-O01_T1w_brain.nii.gz"
    output_file.write_bytes(b"nifti")

    pdf_path = write_technical_pdf(
        tmp_path / "logs" / "technical_report.pdf",
        study_id="study-1",
        bids_subject_id="sub-O01",
        processor_name="compneuro-anatproc",
        processor_version="1.1",
        processor_backend="compneuro",
        status="completed",
        output_files=[output_file],
    )
    zip_path = write_outputs_zip(preproc_dir, tmp_path / "outputs.zip")

    assert pdf_path.exists()
    assert zip_path.exists()
