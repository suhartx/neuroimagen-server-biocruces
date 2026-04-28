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


def test_upload_rejects_invalid_extension(client):
    response = client.post(
        "/api/studies/upload",
        files={"file": ("patient.exe", b"bad", "application/octet-stream")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Extensión de fichero no permitida"
