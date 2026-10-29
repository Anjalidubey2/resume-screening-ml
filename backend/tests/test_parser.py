from __future__ import annotations

import pytest

from services.parser import ResumeParsingError, extract_text_from_bytes


def test_txt_resume_is_parsed_and_whitespace_normalized():
    parsed = extract_text_from_bytes(b"Jane Doe\n\nPython   developer with SQL skills", "jane.txt")
    assert parsed.text == "Jane Doe Python developer with SQL skills"
    assert parsed.word_count == 7
    assert parsed.extension == ".txt"


def test_unsupported_format_is_rejected():
    with pytest.raises(ResumeParsingError, match="Unsupported"):
        extract_text_from_bytes(b"x" * 50, "resume.png")


def test_empty_file_is_rejected():
    with pytest.raises(ResumeParsingError, match="empty"):
        extract_text_from_bytes(b"", "resume.txt")


def test_too_little_text_is_rejected():
    with pytest.raises(ResumeParsingError, match="enough readable text"):
        extract_text_from_bytes(b"hi", "resume.txt")
