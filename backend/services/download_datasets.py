"""Download the public datasets used for training.

Dataset 2 (English resume-job fit pairs) comes from Hugging Face and downloads automatically.
Datasets 1 and 3 are on Kaggle, which needs a free login, so this script tells you where to put them.
"""
from __future__ import annotations

import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

ENGLISH_MATCHING_DIR = RAW_DIR / "dataset_2_resume_job_fit"
ENGLISH_MATCHING_BASE_URL = "https://huggingface.co/datasets/cnamuangtoun/resume-job-description-fit/resolve/main"
ENGLISH_MATCHING_FILES = ["train.csv", "test.csv"]

KAGGLE_DATASETS = [
    (
        "Dataset 1 - Resume Dataset (role classifier)",
        "https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset",
        RAW_DIR / "dataset_1_resumes" / "Resume.csv",
    ),
    (
        "Dataset 3 - AI-Powered Resume Screening Dataset 2025 (screening models)",
        "https://www.kaggle.com/datasets/mdtalhask/ai-powered-resume-screening-dataset-2025",
        RAW_DIR / "dataset_3_ai_screening" / "AI_Resume_Screening.csv",
    ),
]


def download_english_matching_dataset() -> list[Path]:
    ENGLISH_MATCHING_DIR.mkdir(parents=True, exist_ok=True)
    saved = []
    for name in ENGLISH_MATCHING_FILES:
        target = ENGLISH_MATCHING_DIR / name
        if target.exists():
            print(f"Already downloaded: {target}")
        else:
            print(f"Downloading {name} from Hugging Face...")
            urllib.request.urlretrieve(f"{ENGLISH_MATCHING_BASE_URL}/{name}", target)
            print(f"Saved {target} ({target.stat().st_size / 1_000_000:.1f} MB)")
        saved.append(target)
    return saved


def report_kaggle_datasets() -> None:
    for title, url, target in KAGGLE_DATASETS:
        if target.exists():
            print(f"Found: {title}")
        else:
            print(f"Missing: {title}\n  1. Download it from {url}\n  2. Unzip and place the CSV at {target}")


def main() -> None:
    download_english_matching_dataset()
    report_kaggle_datasets()


if __name__ == "__main__":
    main()
