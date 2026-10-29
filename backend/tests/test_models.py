from __future__ import annotations

import pytest

# exc_type=ImportError also skips when a library is installed but cannot load (e.g. blocked by Windows).
pytest.importorskip("numpy", exc_type=ImportError)
pytest.importorskip("sklearn", exc_type=ImportError)

from services.matching_model import predict_match_score  # noqa: E402
from services.model import predict_role  # noqa: E402
from services.recommender import recommend_as_dict  # noqa: E402
from services.screening_model import predict_screening  # noqa: E402

UNRELATED_RESUME = "Head chef with 10 years of kitchen management, menu planning, food safety and catering."


def test_every_trained_model_loads_and_predicts(sample_resume, sample_job):
    roles = predict_role(sample_resume, top_k=3)
    assert len(roles) == 3
    assert 0 <= roles[0]["confidence"] <= 1

    assert 0 <= predict_match_score(sample_resume, sample_job)["match_probability"] <= 1

    screening = predict_screening(
        skills="python, sql, machine learning",
        experience_years=2,
        education="B.Tech",
        certifications="",
        job_role="data scientist",
        projects_count=1,
    )
    assert 0 <= screening["ai_score"] <= 100
    assert screening["decision"] in {"Hire", "Reject"}


def test_recommender_uses_ml_models_not_fallbacks(sample_resume, sample_job):
    result = recommend_as_dict(resume_text=sample_resume, job_text=sample_job)
    assert result["model_sources"] == {"role": "ml", "match": "ml", "screening": "ml"}
    assert result["screening_role"] == "data scientist"
    assert 0 <= result["final_score"] <= 100
    assert result["final_score"] == pytest.approx(sum(result["score_breakdown"].values()), abs=0.01)


def test_relevant_resume_outranks_unrelated_resume(sample_resume, sample_job):
    relevant = recommend_as_dict(resume_text=sample_resume, job_text=sample_job)["final_score"]
    unrelated = recommend_as_dict(resume_text=UNRELATED_RESUME, job_text=sample_job)["final_score"]
    assert relevant > unrelated
