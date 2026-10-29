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
