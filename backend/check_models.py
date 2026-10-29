from __future__ import annotations

import warnings

from services.matching_model import predict_match_score
from services.model import predict_role
from services.screening_model import predict_screening

SAMPLE_RESUME = (
    "Data scientist with 3 years of experience in Python, SQL, machine learning, NLP and "
    "scikit-learn. Built REST APIs with FastAPI and deployed models with Docker on AWS."
)
SAMPLE_JOB = (
    "Hiring a data scientist with Python, SQL, machine learning, NLP, model evaluation, "
    "API development, Docker, and AWS experience."
)

CHECKS = {
    "Role classifier": lambda: predict_role(SAMPLE_RESUME, top_k=3),
    "Resume-job matcher": lambda: predict_match_score(SAMPLE_RESUME, SAMPLE_JOB),
    "Screening models": lambda: predict_screening(
        skills="python, sql, machine learning, nlp",
        experience_years=3,
        education="B.Tech",
        certifications="AWS",
        job_role="data scientist",
        projects_count=2,
    ),
}


def main() -> int:
    failures = 0
    for name, check in CHECKS.items():
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                result = check()
            except Exception as error:
                failures += 1
                print(f"[FAILED] {name}: {type(error).__name__}: {error}")
                continue
        print(f"[OK]     {name}: {result}")
        for warning in {f"{w.category.__name__}: {str(w.message)[:160]}" for w in caught}:
            print(f"         warning -> {warning}")

    if failures:
        print(f"\n{failures} model(s) failed. The app will silently use fallback formulas instead of ML.")
        return 1
    print("\nAll ML models loaded and predicted successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
