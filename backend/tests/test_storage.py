from __future__ import annotations

import csv
from pathlib import Path

from services import export_results, feedback_store


def test_feedback_rows_are_appended_under_one_header(tmp_path, monkeypatch):
    monkeypatch.setattr(feedback_store, "FEEDBACK_DIR", tmp_path)
    monkeypatch.setattr(feedback_store, "FEEDBACK_PATH", tmp_path / "feedback.csv")

    for feedback_type in ("hire", "reject"):
        feedback_store.save_feedback(
            {
                "filename": "cv.txt",
                "feedback_type": feedback_type,
                "role_predictions": [{"role": "hr", "confidence": 0.9}],
                "matched_skills": ["python", "sql"],
            }
        )

    with (tmp_path / "feedback.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [row["feedback_type"] for row in rows] == ["hire", "reject"]
    assert rows[0]["top_role"] == "hr"
    assert rows[0]["matched_skills"] == "python; sql"


def test_rankings_export_writes_rows_in_rank_order(tmp_path, monkeypatch):
    monkeypatch.setattr(export_results, "OUTPUTS_DIR", tmp_path)

    result = export_results.export_rankings(
        [{"filename": "a.pdf", "final_score": 80, "matched_skills": ["python"]}, {"filename": "b.pdf", "final_score": 60}]
    )

    assert result["rows_exported"] == 2
    with Path(result["file_path"]).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [row["rank"] for row in rows] == ["1", "2"]
    assert rows[0]["matched_skills"] == "python"
