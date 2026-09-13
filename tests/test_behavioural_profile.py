"""Tests for analysis.behavioural_profile (Section 10.2's Behavioural
Response Profile: per-category, per-language counts and overlay rates).
"""

from analysis.behavioural_profile import behavioural_profile, overlay_profile


def test_behavioural_profile_groups_by_language():
    rows = [
        {"question_id": "1", "category": "Correct", "language": "en"},
        {"question_id": "2", "category": "Incorrect-Guess", "language": "en"},
        {"question_id": "3", "category": "Correct", "language": "de"},
    ]
    profile = behavioural_profile(rows, group_by=("language",))
    assert profile[("en",)]["Correct"] == 1
    assert profile[("en",)]["Incorrect-Guess"] == 1
    assert profile[("de",)]["Correct"] == 1


def test_overlay_profile_excludes_not_applicable_rows():
    rows = [
        {
            "question_id": "1",
            "category": "Correct",
            "language": "en",
            "jurisdiction_adaptation": "Correct-for-Jurisdiction",
        },
        {
            "question_id": "2",
            "category": "Correct",
            "language": "en",
            "jurisdiction_adaptation": None,
        },
    ]
    profile = overlay_profile(rows, "jurisdiction_adaptation", group_by=("language",))
    assert profile[("en",)]["Correct-for-Jurisdiction"] == 1
    assert sum(profile[("en",)].values()) == 1
