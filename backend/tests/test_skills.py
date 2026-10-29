from __future__ import annotations

from conftest import JOB_DESCRIPTIONS_DIR
from services.skills import calculate_skill_gap, extract_skills, skill_terms


def test_finds_skills_through_synonyms():
    skills = set(extract_skills("Built models with sklearn and PyTorch, served Node.js REST APIs on PostgreSQL."))
    assert {"scikit learn", "pytorch", "javascript", "api development", "sql"} <= skills


def test_ambiguous_everyday_words_do_not_count_as_skills():
    text = "Ann worked on job security, iOS testing, spring semester and a lambda function at a shell company."
    assert extract_skills(text) == []


def test_whole_words_only_so_java_is_not_found_inside_javascript():
    assert "java" not in extract_skills("Frontend work in JavaScript and TypeScript")


def test_cplusplus_and_csharp_survive_text_cleaning():
    assert {"cplusplus", "csharp"} <= set(extract_skills("Wrote C++ services and C# tools on .NET"))


def test_skill_match_score_is_share_of_job_skills_found():
    gap = calculate_skill_gap("Python and SQL developer", "Need Python, SQL, Docker and AWS")
    assert gap.matched_skills == ["python", "sql"]
    assert gap.missing_skills == ["aws", "docker"]
    assert gap.skill_match_score == 0.5


def test_cybersecurity_job_description_skills_are_detected():
    text = (JOB_DESCRIPTIONS_DIR / "cybersecurity_analyst.txt").read_text(encoding="utf-8")
    assert {"networking", "linux", "ethical hacking", "cybersecurity", "cloud security"} <= set(extract_skills(text))


def test_every_sample_job_description_has_enough_skills():
    for path in JOB_DESCRIPTIONS_DIR.glob("*.txt"):
        assert len(extract_skills(path.read_text(encoding="utf-8"))) >= 6, path.name


def test_skill_terms_include_raw_synonyms_for_highlighting():
    assert {"scikit-learn", "sklearn", "c++"} <= set(skill_terms(["scikit learn", "cplusplus"]))
