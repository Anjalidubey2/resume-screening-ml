from __future__ import annotations

import pytest

from conftest import JOB_DESCRIPTIONS_DIR
from services.job_roles import infer_screening_role


@pytest.mark.parametrize(
    ("filename", "role"),
    [
        ("cybersecurity_analyst.txt", "cybersecurity analyst"),
        ("data_scientist.txt", "data scientist"),
        ("full_stack_developer.txt", "software engineer"),
        ("ml_engineer.txt", "ai researcher"),
    ],
)
def test_sample_job_descriptions_map_to_screening_roles(filename, role):
    assert infer_screening_role((JOB_DESCRIPTIONS_DIR / filename).read_text(encoding="utf-8")) == role


def test_earliest_title_wins_when_several_appear():
    assert infer_screening_role("Machine Learning Engineer joining our data science team") == "ai researcher"


def test_skill_overlap_is_used_when_no_title_is_named():
    assert infer_screening_role("Must know React, JavaScript, HTML and CSS.") == "software engineer"


def test_returns_none_when_nothing_fits():
    assert infer_screening_role("Looking for a friendly chef to run our kitchen.") is None
