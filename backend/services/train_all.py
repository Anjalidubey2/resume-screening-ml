"""Retrain every model whose cleaned dataset exists, after backing up the current models."""
from __future__ import annotations

from dataclasses import asdict

from services.data_preparation import MATCHING_OUTPUT, RESUMES_OUTPUT, SCREENING_OUTPUT
from services.matching_model import train_matching_model
from services.model import train_role_classifier
from services.model_registry import create_model_version
from services.screening_model import train_screening_models

PIPELINES = [
    ("Role classifier (dataset 1)", RESUMES_OUTPUT, train_role_classifier),
    ("Resume-job matcher (dataset 2)", MATCHING_OUTPUT, train_matching_model),
    ("Screening models (dataset 3)", SCREENING_OUTPUT, train_screening_models),
]


def main() -> None:
    backup = create_model_version(reason="before_train_all")
    print(f"Backed up current models to {backup['version_dir']}")

    for name, data_path, train in PIPELINES:
        print(f"\n=== {name} ===")
        if not data_path.exists():
            print(f"Skipped: {data_path} not found. Download the dataset, then run: python -m services.data_preparation")
            continue
        result = train()
        for key, value in asdict(result).items():
            print(f"{key}: {value}")

    print("\nDone. Restart the backend so it loads the new models.")


if __name__ == "__main__":
    main()
