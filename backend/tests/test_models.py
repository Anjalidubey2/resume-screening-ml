from __future__ import annotations

import pytest

# exc_type=ImportError also skips when a library is installed but cannot load (e.g. blocked by Windows).
pytest.importorskip("numpy", exc_type=ImportError)
pytest.importorskip("sklearn", exc_type=ImportError)
pytest.importorskip("pdfminer.high_level", exc_type=ImportError)
pytest.importorskip("docx", exc_type=ImportError)

from conftest import JOB_DESCRIPTIONS_DIR, SAMPLE_RESUMES_DIR  # noqa: E402
from services.matching_model import predict_match_score  # noqa: E402
from services.model import predict_role  # noqa: E402
from services.parser import extract_text_from_bytes  # noqa: E402
from services.recommender import recommend_as_dict, warm_up_models  # noqa: E402
from services.screening_model import predict_screening  # noqa: E402

UNRELATED_RESUME = "Head chef with 10 years of kitchen management, menu planning, food safety and catering."
NON_TECH_SAMPLES = {"neha_gupta_accountant.pdf", "vikram_rao_hr_manager.docx"}
BEST_CANDIDATE = {
    "data_scientist": "ananya_sharma_data_scientist.pdf",
    "ml_engineer": "rohit_verma_ml_engineer.docx",
    "full_stack_developer": "priya_nair_full_stack_developer.pdf",
    "cybersecurity_analyst": "arjun_mehta_cybersecurity_analyst.docx",
}


def rank_samples(job: str) -> list[str]:
    """Sample resume file names ordered from best to worst final score for one job description."""
    job_text = (JOB_DESCRIPTIONS_DIR / f"{job}.txt").read_text(encoding="utf-8")
    scores = {}
    for path in SAMPLE_RESUMES_DIR.iterdir():
        if path.suffix in {".pdf", ".docx", ".txt"}:
            text = extract_text_from_bytes(path.read_bytes(), path.name).text
            scores[path.name] = recommend_as_dict(resume_text=text, job_text=job_text)["final_score"]
    return sorted(scores, key=scores.get, reverse=True)


def test_startup_warm_up_loads_every_model():
    assert warm_up_models() == {"role": "loaded", "match": "loaded", "screening": "loaded"}


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


@pytest.mark.parametrize("job", sorted(BEST_CANDIDATE))
def test_matching_candidate_ranks_first_and_non_tech_profiles_rank_low(job):
    ranking = rank_samples(job)
    assert ranking[0] == BEST_CANDIDATE[job], ranking
    assert NON_TECH_SAMPLES <= set(ranking[len(ranking) // 2 :]), ranking
