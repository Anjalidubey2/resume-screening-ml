from __future__ import annotations

import re

from services.preprocessing import basic_clean_text
from services.skills import extract_skills

# The screening models were trained on dataset 3, which only contains these four job roles.
# Each role lists job-title phrases that point to it.
SCREENING_ROLE_TITLES: dict[str, list[str]] = {
    "ai researcher": [
        "ai researcher",
        "research scientist",
        "machine learning engineer",
        "ml engineer",
        "ai engineer",
        "deep learning engineer",
        "nlp engineer",
    ],
    "data scientist": ["data scientist", "data analyst", "data science"],
    "cybersecurity analyst": [
        "cybersecurity analyst",
        "security analyst",
        "soc analyst",
        "penetration tester",
        "cybersecurity",
        "cyber security",
    ],
    "software engineer": [
        "software engineer",
        "software developer",
        "full stack developer",
        "frontend developer",
        "backend developer",
        "web developer",
        "developer",
    ],
}

# Used when the job description names no known title: the role whose skills overlap most wins.
SCREENING_ROLE_SKILLS: dict[str, set[str]] = {
    "ai researcher": {"deep learning", "pytorch", "tensorflow", "nlp", "computer vision", "bert", "llm"},
    "data scientist": {"machine learning", "statistics", "data analysis", "pandas", "sql", "data visualization"},
    "cybersecurity analyst": {"cybersecurity", "ethical hacking", "networking", "linux", "cloud security"},
    "software engineer": {"javascript", "react", "java", "api development", "git", "html", "css", "typescript"},
}

# Role-classifier labels (dataset 1 categories, plus the recommender's keyword-fallback labels)
# that suit each screening role. All four roles are technical, so IT and engineering resumes count.
TECH_FIELDS = {"information technology", "engineering", "data science", "web developer", "devops engineer"}
RELEVANT_FIELDS: dict[str, set[str]] = {role: TECH_FIELDS for role in SCREENING_ROLE_TITLES}

_TITLE_PATTERNS = {
    role: [re.compile(rf"(?<!\w){re.escape(title)}(?!\w)") for title in titles]
    for role, titles in SCREENING_ROLE_TITLES.items()
}


def infer_screening_role(job_text: str) -> str | None:
    """Pick the screening role a job description is hiring for, or None if nothing fits."""
    cleaned = basic_clean_text(job_text)

    first_mention: dict[str, int] = {}
    for role, patterns in _TITLE_PATTERNS.items():
        positions = [match.start() for pattern in patterns if (match := pattern.search(cleaned))]
        if positions:
            first_mention[role] = min(positions)
    if first_mention:
        return min(first_mention, key=first_mention.get)

    job_skills = set(extract_skills(job_text))
    overlaps = {role: len(job_skills & skills) for role, skills in SCREENING_ROLE_SKILLS.items()}
    best_role = max(overlaps, key=overlaps.get)
    return best_role if overlaps[best_role] > 0 else None


def role_relevance(job_role: str | None, role_predictions: list[dict[str, float | str]]) -> float:
    """Probability (0-1) that the resume comes from a field that suits the job.

    Being confidently classified as "HR" must not help an HR resume for a data-science job,
    so only the predictions for relevant fields count. Jobs outside the known roles have no
    field mapping, so the classifier's confidence in its top guess is used instead.
    """
    if not role_predictions:
        return 0.0
    fields = RELEVANT_FIELDS.get(job_role or "")
    if fields is None:
        return float(role_predictions[0]["confidence"])
    relevant = sum(float(p["confidence"]) for p in role_predictions if str(p["role"]).strip().lower() in fields)
    return min(relevant, 1.0)
