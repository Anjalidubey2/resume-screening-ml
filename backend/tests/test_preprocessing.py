from __future__ import annotations

from services.preprocessing import USE_NLTK_CORPORA, basic_clean_text, preprocess_text


def test_contact_details_are_removed():
    cleaned = basic_clean_text("Mail jane.doe@example.com or call +91 98765 43210, see https://example.com/cv")
    assert "@" not in cleaned
    assert "example" not in cleaned
    assert "98765" not in cleaned


def test_tech_tokens_are_normalized_before_punctuation_is_stripped():
    assert basic_clean_text("C++, C# and Node.js") == "cplusplus csharp and nodejs"


def test_preprocessing_matches_how_the_role_classifier_was_trained():
    # Training used only the 21-word built-in stopword list and no lemmatization.
    assert USE_NLTK_CORPORA is False
    assert preprocess_text("The managers were managing their projects for years") == (
        "managers were managing their projects years"
    )
