from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

DATASET_1_PATH = RAW_DIR / "dataset_1_resumes" / "Resume.csv"
DATASET_2_PATH = RAW_DIR / "dataset_2_resume_job_matching" / "train.csv"
DATASET_2_EN_DIR = RAW_DIR / "dataset_2_resume_job_fit"
DATASET_3_PATH = RAW_DIR / "dataset_3_ai_screening" / "AI_Resume_Screening.csv"

RESUMES_OUTPUT = PROCESSED_DIR / "resumes_cleaned.csv"
MATCHING_OUTPUT = PROCESSED_DIR / "matching_cleaned.csv"
SCREENING_OUTPUT = PROCESSED_DIR / "screening_cleaned.csv"

TEXT_CLEAN_RE = re.compile(r"\s+")
HTML_RE = re.compile(r"<[^>]+>")

DATASET_2_RESUME_COLUMNS = [
    "positionName",
    "typicalPosition_cv",
    "academicDegree",
    "skills_cv",
    "hardSkills_cv",
    "softSkills_cv",
    "workExperienceList",
    "experience",
    "educationList",
    "education",
    "languageKnowledge_cv",
    "otherCertificates",
]

DATASET_2_JOB_COLUMNS = [
    "vacancyName",
    "professionalSphereName",
    "skills_vacancy",
    "hardSkills_vacancy",
    "softSkills_vacancy",
    "positionRequirements",
    "qualifications",
    "responsibilities",
    "educationRequirements",
    "experienceRequirements",
    "conditions",
    "otherVacancyBenefit",
    "careerPerspective",
]

DATASET_2_USE_COLUMNS = [
    "idCv",
    "idVacancy",
    "cv_status",
    *DATASET_2_RESUME_COLUMNS,
    *DATASET_2_JOB_COLUMNS,
]

STATUS_MAP = {
    "приглашение": 1,
    "отказ": 0,
    "invitation": 1,
    "accept": 1,
    "accepted": 1,
    "hire": 1,
    "reject": 0,
    "rejected": 0,
}

# "Potential Fit" counts as a match: the candidate is worth an interview.
FIT_LABEL_MAP = {
    "good fit": 1,
    "potential fit": 1,
    "no fit": 0,
}

DECISION_MAP = {
    "hire": 1,
    "shortlist": 1,
    "shortlisted": 1,
    "accept": 1,
    "accepted": 1,
    "reject": 0,
    "rejected": 0,
}


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value)
    text = HTML_RE.sub(" ", text)
    text = text.replace("\\n", " ").replace("\n", " ").replace("\r", " ")
    text = TEXT_CLEAN_RE.sub(" ", text).strip()
    return text


def clean_category(value: object) -> str:
    return clean_text(value).strip().lower().replace("-", " ")


def combine_text_columns(frame: pd.DataFrame, columns: Iterable[str]) -> pd.Series:
    available = [column for column in columns if column in frame.columns]
    if not available:
        return pd.Series([""] * len(frame), index=frame.index)
    cleaned = frame[available].map(clean_text)
    return cleaned.apply(lambda row: " ".join(part for part in row if part), axis=1)


def normalize_binary_label(value: object, mapping: dict[str, int]) -> int | None:
    text = clean_text(value).casefold()
    if text in mapping:
        return mapping[text]
    return None


def prepare_resume_dataset(input_path: Path = DATASET_1_PATH, output_path: Path = RESUMES_OUTPUT) -> pd.DataFrame:
    frame = pd.read_csv(input_path, usecols=["ID", "Resume_str", "Category"])
    output = pd.DataFrame(
        {
            "resume_id": frame["ID"].astype(str),
            "resume_text": frame["Resume_str"].map(clean_text),
            "category": frame["Category"].map(clean_category),
        }
    )
    output = output.dropna(subset=["resume_text", "category"])
    output = output[(output["resume_text"] != "") & (output["category"] != "")]
    output = output.drop_duplicates(subset=["resume_id"]).reset_index(drop=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_path, index=False, encoding="utf-8")
    return output


def prepare_matching_dataset(
    input_path: Path = DATASET_2_PATH,
    output_path: Path = MATCHING_OUTPUT,
    chunksize: int = 50_000,
    max_rows: int | None = None,
) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    rows_written = 0
    header = True

    reader = pd.read_csv(
        input_path,
        sep="|",
        usecols=lambda column: column in DATASET_2_USE_COLUMNS,
        chunksize=chunksize,
        low_memory=False,
    )

    for chunk in reader:
        prepared = pd.DataFrame(
            {
                "resume_id": chunk["idCv"].astype(str),
                "job_id": chunk["idVacancy"].astype(str),
                "resume_text": combine_text_columns(chunk, DATASET_2_RESUME_COLUMNS),
                "job_text": combine_text_columns(chunk, DATASET_2_JOB_COLUMNS),
                "match_label": chunk["cv_status"].map(lambda value: normalize_binary_label(value, STATUS_MAP)),
                "raw_status": chunk["cv_status"].map(clean_text),
            }
        )
        prepared = prepared.dropna(subset=["match_label"])
        prepared = prepared[(prepared["resume_text"] != "") & (prepared["job_text"] != "")]
        prepared["match_label"] = prepared["match_label"].astype(int)

        if max_rows is not None:
            remaining = max_rows - rows_written
            if remaining <= 0:
                break
            prepared = prepared.head(remaining)

        if not prepared.empty:
            prepared.to_csv(output_path, mode="a", header=header, index=False, encoding="utf-8")
            rows_written += len(prepared)
            header = False

        if max_rows is not None and rows_written >= max_rows:
            break

    return rows_written


def prepare_screening_dataset(input_path: Path = DATASET_3_PATH, output_path: Path = SCREENING_OUTPUT) -> pd.DataFrame:
    frame = pd.read_csv(input_path)
    output = pd.DataFrame(
        {
            "resume_id": frame["Resume_ID"].astype(str),
            "candidate_name": frame["Name"].map(clean_text),
            "skills": frame["Skills"].map(clean_text),
            "experience_years": pd.to_numeric(frame["Experience (Years)"], errors="coerce").fillna(0),
            "education": frame["Education"].map(clean_text),
            "certifications": frame["Certifications"].map(clean_text),
            "job_role": frame["Job Role"].map(clean_category),
            "decision": frame["Recruiter Decision"].map(clean_text),
            "decision_label": frame["Recruiter Decision"].map(lambda value: normalize_binary_label(value, DECISION_MAP)),
            "salary_expectation": pd.to_numeric(frame["Salary Expectation ($)"], errors="coerce"),
            "projects_count": pd.to_numeric(frame["Projects Count"], errors="coerce").fillna(0).astype(int),
            "ai_score": pd.to_numeric(frame["AI Score (0-100)"], errors="coerce"),
        }
    )
    output = output.dropna(subset=["decision_label", "ai_score"])
    output["decision_label"] = output["decision_label"].astype(int)
    output = output.reset_index(drop=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_path, index=False, encoding="utf-8")
    return output


def prepare_english_matching_dataset(
    input_dir: Path = DATASET_2_EN_DIR,
    output_path: Path = MATCHING_OUTPUT,
) -> pd.DataFrame:
    """English resume-job pairs from Hugging Face (cnamuangtoun/resume-job-description-fit).

    Replaces the Russian dataset 2 so the matcher learns from English text like the resumes it scores.
    """
    paths = sorted(input_dir.glob("*.csv"))
    if not paths:
        raise FileNotFoundError(f"No CSV files found in {input_dir}. Run: python -m services.download_datasets")
    frame = pd.concat([pd.read_csv(path) for path in paths], ignore_index=True)

    output = pd.DataFrame(
        {
            "resume_id": [f"fit_{index}" for index in range(len(frame))],
            "job_id": [f"fit_{index}" for index in range(len(frame))],
            "resume_text": frame["resume_text"].map(clean_text),
            "job_text": frame["job_description_text"].map(clean_text),
            "match_label": frame["label"].map(lambda value: normalize_binary_label(value, FIT_LABEL_MAP)),
            "raw_status": frame["label"].map(clean_text),
        }
    )
    output = output.dropna(subset=["match_label"])
    output = output[(output["resume_text"] != "") & (output["job_text"] != "")]
    output["match_label"] = output["match_label"].astype(int)
    output = output.drop_duplicates(subset=["resume_text", "job_text"]).reset_index(drop=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_path, index=False, encoding="utf-8")
    return output


def write_summary(summary: dict[str, int]) -> Path:
    summary_path = PROCESSED_DIR / "data_preparation_summary.csv"
    pd.DataFrame([summary]).to_csv(summary_path, index=False, encoding="utf-8")
    return summary_path


def prepare_all(
    chunksize: int = 50_000,
    matching_max_rows: int | None = None,
    matching_source: str = "english",
) -> dict[str, int]:
    """Prepare every dataset that has been downloaded; missing ones are skipped with a message."""
    summary: dict[str, int] = {}

    if DATASET_1_PATH.exists():
        resumes = prepare_resume_dataset()
        summary["resumes_cleaned_rows"] = len(resumes)
        summary["resume_categories"] = resumes["category"].nunique()
    else:
        print(f"Skipping dataset 1 (not found): {DATASET_1_PATH}")

    if matching_source == "english":
        if any(DATASET_2_EN_DIR.glob("*.csv")):
            summary["matching_cleaned_rows"] = len(prepare_english_matching_dataset())
        else:
            print(f"Skipping dataset 2 English (not found): {DATASET_2_EN_DIR}")
    elif DATASET_2_PATH.exists():
        summary["matching_cleaned_rows"] = prepare_matching_dataset(chunksize=chunksize, max_rows=matching_max_rows)
    else:
        print(f"Skipping dataset 2 Russian (not found): {DATASET_2_PATH}")

    if DATASET_3_PATH.exists():
        screening = prepare_screening_dataset()
        summary["screening_cleaned_rows"] = len(screening)
        summary["screening_roles"] = screening["job_role"].nunique()
    else:
        print(f"Skipping dataset 3 (not found): {DATASET_3_PATH}")

    if summary:
        write_summary(summary)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare raw resume-screening datasets.")
    parser.add_argument("--chunksize", type=int, default=50_000, help="Chunk size for the large matching dataset.")
    parser.add_argument(
        "--matching-max-rows",
        type=int,
        default=None,
        help="Optional cap for quick experiments with the large matching dataset.",
    )
    parser.add_argument(
        "--matching-source",
        choices=["english", "russian"],
        default="english",
        help="Which resume-job matching dataset to prepare (default: english).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = prepare_all(
        chunksize=args.chunksize,
        matching_max_rows=args.matching_max_rows,
        matching_source=args.matching_source,
    )
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
