"""Language filtering for the corpus_b task family (Set B, RQ2)."""

from functools import partial


def filter_language(dataset, language):
    return dataset.filter(lambda row: row["language"] == language)


filter_en = partial(filter_language, language="en")
filter_de = partial(filter_language, language="de")
filter_sw = partial(filter_language, language="sw")
filter_bn = partial(filter_language, language="bn")
