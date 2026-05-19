import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from app.services.storage import LocalStudyStorage


@dataclass(frozen=True)
class BidsStudyPaths:
    bids_project_dir: Path
    bids_data_dir: Path
    t1w_path: Path
    participants_path: Path
    dataset_description_path: Path


def prepare_single_subject_t1w_bids(
    storage: LocalStudyStorage,
    study_id: UUID,
    source_file: Path,
    bids_subject_id: str,
) -> BidsStudyPaths:
    bids_data_dir = storage.bids_data_dir(study_id)
    subject_anat_dir = bids_data_dir / bids_subject_id / "anat"
    subject_anat_dir.mkdir(parents=True, exist_ok=True)

    t1w_path = subject_anat_dir / f"{bids_subject_id}_T1w.nii.gz"
    shutil.copy2(source_file, t1w_path)

    participants_path = bids_data_dir / "participants.tsv"
    participants_path.write_text(f"participant_id\n{bids_subject_id}\n", encoding="utf-8")

    dataset_description_path = bids_data_dir / "dataset_description.json"
    dataset_description_path.write_text(
        json.dumps(
            {
                "Name": "neuroimagen-server-biocruces study",
                "BIDSVersion": "1.11.1",
                "DatasetType": "raw",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return BidsStudyPaths(
        bids_project_dir=storage.bids_project_dir(study_id),
        bids_data_dir=bids_data_dir,
        t1w_path=t1w_path,
        participants_path=participants_path,
        dataset_description_path=dataset_description_path,
    )
