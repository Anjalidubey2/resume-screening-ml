from __future__ import annotations

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
JOB_DESCRIPTIONS_DIR = PROJECT_ROOT / "data" / "raw" / "job_descriptions"
SAMPLE_RESUMES_DIR = PROJECT_ROOT / "data" / "samples" / "resumes"


@pytest.fixture
def sample_resume() -> str:
    return (
        "Data scientist with 3 years of experience in Python, SQL, machine learning, NLP and "
        "scikit-learn. Built REST APIs with FastAPI and deployed models with Docker on AWS."
    )


@pytest.fixture
def sample_job() -> str:
    return (JOB_DESCRIPTIONS_DIR / "data_scientist.txt").read_text(encoding="utf-8")
