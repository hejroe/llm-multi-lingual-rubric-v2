"""Language filtering for the corpus_e task family (Set E, RQ6).

Added corpus-v0.3 (2026-09-15): set_e.csv gained a `language` column and
German rows once English-only stopped being enough for RQ6 to have any
primary-language (German, 10.5) comparison at all. Mirrors corpus_b/c's
own filter_language pattern.
"""

from functools import partial


def filter_language(dataset, language):
    return dataset.filter(lambda row: row["language"] == language)


filter_en = partial(filter_language, language="en")
filter_de = partial(filter_language, language="de")
