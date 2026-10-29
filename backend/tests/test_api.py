from __future__ import annotations

import pytest

# exc_type=ImportError also skips when a library is installed but cannot load (e.g. blocked by Windows).
pytest.importorskip("numpy", exc_type=ImportError)
pytest.importorskip("fastapi", exc_type=ImportError)
pytest.importorskip("httpx", exc_type=ImportError)

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402

client = TestClient(app)


def test_health_check():
    assert client.get("/health").json() == {"status": "ok"}


def test_recommend_upload_scores_a_txt_resume(sample_resume, sample_job):
    response = client.post(
        "/api/recommend-upload",
        files={"file": ("candidate.txt", sample_resume.encode("utf-8"), "text/plain")},
        data={"job_text": sample_job},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "candidate.txt"
    assert body["resume_text"].startswith("Data scientist")
    assert set(body["model_sources"]) == {"role", "match", "screening"}
    assert "python" in body["matched_skills"]


def test_unsupported_upload_returns_400(sample_job):
    response = client.post(
        "/api/recommend-upload",
        files={"file": ("photo.png", b"x" * 50, "image/png")},
        data={"job_text": sample_job},
    )
    assert response.status_code == 400
    assert "Unsupported" in response.json()["detail"]
