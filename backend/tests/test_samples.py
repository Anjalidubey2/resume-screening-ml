from __future__ import annotations

import pytest

from conftest import JOB_DESCRIPTIONS_DIR, SAMPLE_RESUMES_DIR
from services.parser import ParsedResume, extract_text_from_bytes
from services.skills import calculate_skill_gap

SAMPLES = sorted(path for path in SAMPLE_RESUMES_DIR.iterdir() if path.suffix in {".pdf", ".docx", ".txt"})
READER_MODULES = {".pdf": "pdfminer.high_level", ".docx": "docx"}


def read_sample(path) -> ParsedResume:
    if path.suffix in READER_MODULES:
        # exc_type=ImportError also skips when the reader is installed but blocked from loading.
        pytest.importorskip(READER_MODULES[path.suffix], exc_type=ImportError)
    return extract_text_from_bytes(path.read_bytes(), path.name)


def test_demo_kit_has_every_file_type():
    assert {path.suffix for path in SAMPLES} == {".pdf", ".docx", ".txt"}


@pytest.mark.parametrize("path", SAMPLES, ids=lambda path: path.name)
def test_sample_resume_is_readable(path):
    parsed = read_sample(path)
    assert parsed.word_count > 40
    assert "@example.com" in parsed.text


@pytest.mark.parametrize(
    ("job", "best_candidate"),
    [
        ("data_scientist", "ananya_sharma_data_scientist.pdf"),
        ("ml_engineer", "rohit_verma_ml_engineer.docx"),
        ("full_stack_developer", "priya_nair_full_stack_developer.pdf"),
        ("cybersecurity_analyst", "arjun_mehta_cybersecurity_analyst.docx"),
    ],
)
def test_matching_candidate_has_the_best_skill_score(job, best_candidate):
    job_text = (JOB_DESCRIPTIONS_DIR / f"{job}.txt").read_text(encoding="utf-8")
    scores = {path.name: calculate_skill_gap(read_sample(path).text, job_text).skill_match_score for path in SAMPLES}
    assert max(scores, key=scores.get) == best_candidate
