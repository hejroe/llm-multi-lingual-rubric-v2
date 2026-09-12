"""Variety filtering and MCQ rendering for the corpus_f task family (Set F, RQ7)."""

from functools import partial

_CHOICE_LETTERS = "ABCDEFGHIJ"


def filter_variety(dataset, variety):
    return dataset.filter(lambda row: row["variety"] == variety)


filter_uk = partial(filter_variety, variety="UK")
filter_au = partial(filter_variety, variety="AU")


def format_mcq(doc):
    lines = [f"Question: {doc['question_text']}"]
    for i in range(10):
        option_text = doc.get(f"option_{i}")
        if option_text:
            lines.append(f"{_CHOICE_LETTERS[i]}. {option_text}")
    lines.append("Answer:")
    return "\n".join(lines)
