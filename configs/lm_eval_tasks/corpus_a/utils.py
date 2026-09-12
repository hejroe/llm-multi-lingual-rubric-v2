"""Doc filtering and MCQ rendering for the corpus_a task family.

corpus/vX.Y/set_a.csv (STUDY_PROTOCOL.md 5.5, Set A) mixes two shapes of
item in one file: `domain: knowledge` (MMLU-ProX-sourced, multiple choice,
`option_0..option_9`) and `domain: procedural` (MGSM-Rev2-sourced, free-text
numeric answer, no options) — each language further mixed in the same file.
`process_docs` below filters to one (domain, language) cell per task; the
MCQ rendering mirrors the stock `mmlu_prox` task's option-lettering
convention (a-j) without adopting its 5-shot chain-of-thought prompting,
since this project's own rubric (Section 8) scores the raw free-text
response directly rather than relying on lm-eval-harness's own
`answer is (X)` extraction convention.
"""

from functools import partial

_CHOICE_LETTERS = "ABCDEFGHIJ"


def filter_domain_language(dataset, domain, language):
    return dataset.filter(lambda row: row["domain"] == domain and row["language"] == language)


filter_knowledge_en = partial(filter_domain_language, domain="knowledge", language="en")
filter_knowledge_de = partial(filter_domain_language, domain="knowledge", language="de")
filter_knowledge_sw = partial(filter_domain_language, domain="knowledge", language="sw")
filter_knowledge_bn = partial(filter_domain_language, domain="knowledge", language="bn")

filter_procedural_en = partial(filter_domain_language, domain="procedural", language="en")
filter_procedural_de = partial(filter_domain_language, domain="procedural", language="de")
filter_procedural_sw = partial(filter_domain_language, domain="procedural", language="sw")
filter_procedural_bn = partial(filter_domain_language, domain="procedural", language="bn")


def format_mcq(doc, question_label="Question", answer_label="Answer"):
    lines = [f"{question_label}: {doc['question_text']}"]
    for i in range(10):
        option_text = doc.get(f"option_{i}")
        if option_text:
            lines.append(f"{_CHOICE_LETTERS[i]}. {option_text}")
    lines.append(f"{answer_label}:")
    return "\n".join(lines)


format_mcq_en = partial(format_mcq, question_label="Question", answer_label="Answer")
format_mcq_de = partial(format_mcq, question_label="Frage", answer_label="Antwort")
format_mcq_sw = partial(format_mcq, question_label="Swali", answer_label="Answer")
format_mcq_bn = partial(format_mcq, question_label="প্রশ্ন", answer_label="Answer")
