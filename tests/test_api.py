def test_healthcheck(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_creates_study(client):
    response = client.post(
        "/api/studies/upload",
        files={"file": ("study.nii", b"dummy image", "application/octet-stream")},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "queued"

    list_response = client.get("/api/studies")
    assert list_response.status_code == 200
    studies = list_response.json()
    assert len(studies) == 1
    assert studies[0]["original_filename"] == "study.nii"
    assert studies[0]["has_output_zip"] is False


def test_upload_rejects_invalid_extension(client):
    response = client.post(
        "/api/studies/upload",
        files={"file": ("patient.exe", b"bad", "application/octet-stream")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Extensión de fichero no permitida"


def test_upload_accepts_optional_bids_subject_id(client):
    response = client.post(
        "/api/studies/upload",
        files={"file": ("study.nii.gz", b"dummy image", "application/octet-stream")},
        data={"bids_subject_id": "sub-O01"},
    )

    assert response.status_code == 201
    assert response.json()["bids_subject_id"] == "sub-O01"

    studies = client.get("/api/studies").json()
    assert studies[0]["bids_subject_id"] == "sub-O01"


def test_compneuro_upload_rejects_non_nifti_gz(compneuro_client):
    response = compneuro_client.post(
        "/api/studies/upload",
        files={"file": ("study.nii", b"dummy image", "application/octet-stream")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Para compneuro-anatproc se espera un fichero .nii.gz"


def test_compneuro_upload_generates_bids_subject(compneuro_client):
    response = compneuro_client.post(
        "/api/studies/upload",
        files={"file": ("study.nii.gz", b"dummy image", "application/octet-stream")},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["bids_subject_id"].startswith("sub-")

    studies = compneuro_client.get("/api/studies").json()
    assert studies[0]["processor_backend"] == "compneuro"
    assert studies[0]["bids_subject_id"] == payload["bids_subject_id"]


def test_compneuro_upload_cleans_storage_when_bids_preparation_fails(compneuro_client, monkeypatch):
    def fail_bids_preparation(*args, **kwargs):
        raise RuntimeError("forced failure")

    import app.api.routes as routes

    monkeypatch.setattr(routes, "prepare_single_subject_t1w_bids", fail_bids_preparation)

    response = compneuro_client.post(
        "/api/studies/upload",
        files={"file": ("study.nii.gz", b"dummy image", "application/octet-stream")},
    )

    assert response.status_code == 500
    assert compneuro_client.get("/api/studies").json() == []
