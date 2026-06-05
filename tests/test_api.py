from pathlib import Path
from uuid import UUID

from app.models.audit_event import AuditEvent
from app.models.study import Study, StudyStatus
from app.models.user import User, UserRole
from app.services.auth import hash_password, normalize_email


def test_healthcheck(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_returns_token_and_records_audit_event(client):
    create_test_user(
        client, "admin@example.org", "secret-pass", role=UserRole.admin.value
    )

    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.org", "password": "secret-pass"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]
    assert payload["user"]["role"] == "admin"

    db = client.app.state.testing_session_local()
    event = (
        db.query(AuditEvent).filter(AuditEvent.event_type == "login_succeeded").one()
    )
    assert event.actor == "admin@example.org"
    assert event.actor_user_id is not None
    db.close()


def test_login_rejects_invalid_password(client):
    create_test_user(client, "researcher@example.org", "secret-pass")

    response = client.post(
        "/api/auth/login",
        json={"email": "researcher@example.org", "password": "bad-pass"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales no válidas"


def test_unauthenticated_user_cannot_access_protected_studies(client):
    response = client.get("/api/studies")

    assert response.status_code == 401


def test_upload_creates_owned_study_and_audit_event(client):
    headers, user_id = auth_headers(client, "researcher@example.org", "secret-pass")

    response = client.post(
        "/api/studies/upload",
        files={"file": ("study.nii", b"dummy image", "application/octet-stream")},
        headers=headers,
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "queued"

    list_response = client.get("/api/studies", headers=headers)
    assert list_response.status_code == 200
    studies = list_response.json()
    assert len(studies) == 1
    assert studies[0]["original_filename"] == "study.nii"
    assert studies[0]["owner_user_id"] == str(user_id)
    assert studies[0]["has_output_zip"] is False

    db = client.app.state.testing_session_local()
    event = db.query(AuditEvent).filter(AuditEvent.event_type == "study_uploaded").one()
    assert event.actor_user_id == user_id
    db.close()


def test_upload_rejects_invalid_extension(client):
    headers, _ = auth_headers(client, "researcher@example.org", "secret-pass")

    response = client.post(
        "/api/studies/upload",
        files={"file": ("patient.exe", b"bad", "application/octet-stream")},
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Extensión de fichero no permitida"


def test_upload_accepts_optional_bids_subject_id(client):
    headers, _ = auth_headers(client, "researcher@example.org", "secret-pass")

    response = client.post(
        "/api/studies/upload",
        files={"file": ("study.nii.gz", b"dummy image", "application/octet-stream")},
        data={"bids_subject_id": "sub-O01"},
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json()["bids_subject_id"] == "sub-O01"

    studies = client.get("/api/studies", headers=headers).json()
    assert studies[0]["bids_subject_id"] == "sub-O01"


def test_researcher_only_sees_own_studies_and_admin_sees_all(client):
    researcher_headers, _ = auth_headers(
        client, "researcher@example.org", "secret-pass"
    )
    other_headers, _ = auth_headers(client, "other@example.org", "secret-pass")
    admin_headers, _ = auth_headers(
        client, "admin@example.org", "secret-pass", role=UserRole.admin.value
    )

    client.post(
        "/api/studies/upload",
        files={"file": ("own.nii", b"dummy image", "application/octet-stream")},
        headers=researcher_headers,
    )
    client.post(
        "/api/studies/upload",
        files={"file": ("other.nii", b"dummy image", "application/octet-stream")},
        headers=other_headers,
    )

    own_studies = client.get("/api/studies", headers=researcher_headers).json()
    admin_studies = client.get("/api/studies", headers=admin_headers).json()

    assert [study["original_filename"] for study in own_studies] == ["own.nii"]
    assert {study["original_filename"] for study in admin_studies} == {
        "own.nii",
        "other.nii",
    }


def test_non_owner_cannot_view_or_download_study(client):
    owner_headers, _ = auth_headers(client, "owner@example.org", "secret-pass")
    other_headers, _ = auth_headers(client, "other@example.org", "secret-pass")

    response = client.post(
        "/api/studies/upload",
        files={"file": ("study.nii", b"dummy image", "application/octet-stream")},
        headers=owner_headers,
    )
    study_id = response.json()["id"]

    db = client.app.state.testing_session_local()
    study = db.get(Study, UUID(study_id))
    report_path = Path(study.output_path) / "reports" / "technical_report.pdf"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_bytes(b"%PDF-1.4\n%%EOF\n")
    study.status = StudyStatus.completed
    study.pdf_path = str(report_path)
    db.commit()
    db.close()

    detail = client.get(f"/api/studies/{study_id}", headers=other_headers)
    download = client.get(
        f"/api/studies/{study_id}/download/pdf", headers=other_headers
    )

    assert detail.status_code == 404
    assert download.status_code == 404


def test_owner_can_download_completed_report(client):
    headers, _ = auth_headers(client, "researcher@example.org", "secret-pass")
    response = client.post(
        "/api/studies/upload",
        files={"file": ("study.nii", b"dummy image", "application/octet-stream")},
        headers=headers,
    )
    study_id = response.json()["id"]

    db = client.app.state.testing_session_local()
    study = db.get(Study, UUID(study_id))
    report_path = Path(study.output_path) / "reports" / "technical_report.pdf"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_bytes(b"%PDF-1.4\n%%EOF\n")
    study.status = StudyStatus.completed
    study.pdf_path = str(report_path)
    db.commit()
    db.close()

    download = client.get(f"/api/studies/{study_id}/download/pdf", headers=headers)

    assert download.status_code == 200
    assert download.headers["content-type"] == "application/pdf"


def test_admin_can_create_researcher_user(client):
    admin_headers, _ = auth_headers(
        client, "admin@example.org", "secret-pass", role=UserRole.admin.value
    )

    response = client.post(
        "/api/users",
        json={
            "email": "new@example.org",
            "full_name": "Nuevo Usuario",
            "password": "new-secret",
            "role": "researcher",
        },
        headers=admin_headers,
    )

    assert response.status_code == 201
    assert response.json()["email"] == "new@example.org"
    assert response.json()["role"] == "researcher"


def test_researcher_cannot_create_users(client):
    headers, _ = auth_headers(client, "researcher@example.org", "secret-pass")

    response = client.post(
        "/api/users",
        json={
            "email": "new@example.org",
            "full_name": "Nuevo Usuario",
            "password": "new-secret",
            "role": "researcher",
        },
        headers=headers,
    )

    assert response.status_code == 403


def test_compneuro_upload_rejects_non_nifti_gz(compneuro_client):
    headers, _ = auth_headers(compneuro_client, "researcher@example.org", "secret-pass")
    response = compneuro_client.post(
        "/api/studies/upload",
        files={"file": ("study.nii", b"dummy image", "application/octet-stream")},
        headers=headers,
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Para compneuro-anatproc se espera un fichero .nii.gz"
    )


def test_compneuro_upload_generates_bids_subject(compneuro_client):
    headers, _ = auth_headers(compneuro_client, "researcher@example.org", "secret-pass")
    response = compneuro_client.post(
        "/api/studies/upload",
        files={"file": ("study.nii.gz", b"dummy image", "application/octet-stream")},
        headers=headers,
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["bids_subject_id"].startswith("sub-")

    studies = compneuro_client.get("/api/studies", headers=headers).json()
    assert studies[0]["processor_backend"] == "compneuro"
    assert studies[0]["bids_subject_id"] == payload["bids_subject_id"]


def test_compneuro_upload_cleans_storage_when_bids_preparation_fails(
    compneuro_client, monkeypatch
):
    headers, _ = auth_headers(compneuro_client, "researcher@example.org", "secret-pass")

    def fail_bids_preparation(*args, **kwargs):
        raise RuntimeError("forced failure")

    import app.api.routes as routes

    monkeypatch.setattr(
        routes, "prepare_single_subject_t1w_bids", fail_bids_preparation
    )

    response = compneuro_client.post(
        "/api/studies/upload",
        files={"file": ("study.nii.gz", b"dummy image", "application/octet-stream")},
        headers=headers,
    )

    assert response.status_code == 500
    assert compneuro_client.get("/api/studies", headers=headers).json() == []


def create_test_user(
    client, email: str, password: str, role: str = UserRole.researcher.value
):
    db = client.app.state.testing_session_local()
    user = User(
        email=normalize_email(email),
        full_name="Test User",
        hashed_password=hash_password(password),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    user_id = user.id
    db.close()
    return user_id


def auth_headers(
    client, email: str, password: str, role: str = UserRole.researcher.value
):
    user_id = create_test_user(client, email, password, role=role)
    response = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}, user_id
