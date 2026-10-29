from __future__ import annotations

import pytest

# exc_type=ImportError also skips when a library is installed but cannot load (e.g. blocked by Windows).
pd = pytest.importorskip("pandas", exc_type=ImportError)

from services.data_preparation import prepare_english_matching_dataset  # noqa: E402


def test_english_matching_dataset_is_cleaned_and_labelled(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    pd.DataFrame(
        {
            "resume_text": ["<b>Python</b> developer", "Python developer", "Sales associate", "Nurse", ""],
            "job_description_text": ["Python role", "Python role", "Python role", "Data role", "Empty"],
            "label": ["Good Fit", "Good Fit", "No Fit", "Potential Fit", "No Fit"],
        }
    ).to_csv(raw_dir / "train.csv", index=False)

    output = prepare_english_matching_dataset(input_dir=raw_dir, output_path=tmp_path / "matching.csv")

    assert output["resume_text"].tolist() == ["Python developer", "Sales associate", "Nurse"]
    assert output["match_label"].tolist() == [1, 0, 1]
    assert (tmp_path / "matching.csv").exists()
