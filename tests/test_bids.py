from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.services.bids import prepare_single_subject_t1w_bids
from app.services.security import resolve_bids_subject_id
from app.services.storage import LocalStudyStorage


def test_resolve_bids_subject_id_generates_safe_default():
    study_id = uuid4()

    subject_id = resolve_bids_subject_id("", study_id)

    assert subject_id == f"sub-{study_id.hex[:8]}"


def test_resolve_bids_subject_id_rejects_invalid_value():
    with pytest.raises(HTTPException):
        resolve_bids_subject_id("patient 01", uuid4())


def test_prepare_single_subject_t1w_bids(tmp_path):
    storage = LocalStudyStorage(tmp_path / "studies")
    study_id = uuid4()
    source = tmp_path / "source.nii.gz"
    source.write_bytes(b"nifti")

    paths = prepare_single_subject_t1w_bids(storage, study_id, source, "sub-O01")

    assert paths.t1w_path.exists()
    assert paths.t1w_path.name == "sub-O01_T1w.nii.gz"
    assert paths.participants_path.read_text(encoding="utf-8") == "participant_id\nsub-O01\n"
    assert paths.dataset_description_path.exists()
