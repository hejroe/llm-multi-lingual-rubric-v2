from analysis.reliability import compute_reliability


def test_full_agreement_across_replicates():
    rows = [
        {"question_id": "A-1", "model_name": "m", "category": "Correct"},
        {"question_id": "A-1", "model_name": "m", "category": "Correct"},
        {"question_id": "A-1", "model_name": "m", "category": "Correct"},
    ]
    result = compute_reliability(rows)
    assert result[("m",)].n_items == 1
    assert result[("m",)].n_fully_agreeing == 1
    assert result[("m",)].agreement_rate == 1.0


def test_disagreement_across_replicates():
    rows = [
        {"question_id": "A-1", "model_name": "m", "category": "Correct"},
        {"question_id": "A-1", "model_name": "m", "category": "Incorrect-Guess"},
        {"question_id": "A-2", "model_name": "m", "category": "IDK"},
        {"question_id": "A-2", "model_name": "m", "category": "IDK"},
    ]
    result = compute_reliability(rows)
    assert result[("m",)].n_items == 2
    assert result[("m",)].n_fully_agreeing == 1
    assert result[("m",)].agreement_rate == 0.5


def test_grouped_by_additional_condition():
    rows = [
        {"question_id": "A-1", "model_name": "m", "language": "en", "category": "Correct"},
        {"question_id": "A-1", "model_name": "m", "language": "en", "category": "Correct"},
        {"question_id": "A-1", "model_name": "m", "language": "de", "category": "IDK"},
        {"question_id": "A-1", "model_name": "m", "language": "de", "category": "Correct"},
    ]
    result = compute_reliability(rows, group_by=("model_name", "language"))
    assert result[("m", "en")].agreement_rate == 1.0
    assert result[("m", "de")].agreement_rate == 0.0
