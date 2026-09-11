# Corpus v0.2

Supersedes `corpus/v0.1/` for Set B and Set C only, per Study Protocol
5.8's versioning rule: an expanded family produces a new corpus version
rather than editing the existing one, so any result already measured
against v0.1 keeps citing the exact version it was measured against.
`v0.1` is left untouched and still exists as a valid, citable snapshot.

## What changed from v0.1

- **Set B**: expanded from 1 fact (3 rows) to 10 facts (30 English rows),
  and translated into German, Swahili and Bengali (120 rows total).
- **Set C**: expanded from 1 fact (2 rows) to 10 facts (20 English rows),
  and translated into the same three languages (80 rows total).
- **Set A, Set E, Set F**: unchanged — copied forward from v0.1 as-is
  (Set E's `review_status` reflects the acceptance recorded 2026-09-09;
  see `docs/STUDY_PROTOCOL.md` Appendix A.4).

## Why 10 facts, not 1

McNemar's exact test and the Clopper-Pearson intervals Section 10.3
specifies for RQ2 and RQ3 are paired/proportion methods: run against a
single fact, they have essentially no way to distinguish a real effect
from noise — one paired observation (before three replications) is not
enough for either method to do its job. Ten facts per family is a
practical middle ground: large enough that the analysis genuinely runs
against a non-degenerate sample and its behaviour can be checked, still
inside 5.1's "coverage, not volume" framing (compare 11.5's 2-4 item
accommodation), and achievable with individually-verified primary
sources rather than a large batch produced without real research behind
each one. It is not a claim that ten items give RQ2/RQ3 adequate
statistical power for a confirmatory result — Section 12.2 already states
that limitation and this release doesn't change it — only that the
tests can now be demonstrated running on real, varied data rather than a
single toy case.

## Provenance — Set B (10 facts, sourced 2026-09-09)

Each fact is drawn from a primary or authoritative near-primary source:

| Fact | Jurisdictions compared | Primary source(s) |
|---|---|---|
| Alcohol purchase age | UK (18) / US (21) | Licensing Act 2003 s.146(1); 23 U.S.C. Section 158 |
| Age of criminal responsibility | England & Wales (10) / Germany (14) | Children and Young Persons Act 1933 s.50 (as amended); StGB Section 19 |
| Standard VAT rate | UK (20%) / Germany (19%) | Value Added Tax Act 1994; Umsatzsteuergesetz Section 12 |
| Side of the road | UK (left) / Germany (right) | UK driving convention; StVO Section 2 |
| National voting age | Austria (16) / UK (18) | Austrian electoral law (2007 reform); Representation of the People Act 1983 |
| Tobacco purchase age | UK (18) / US (21) | Children and Young Persons Act 1933 s.7 (as amended 2007); Tobacco 21 (effective 20 Dec 2019) |
| Drink-drive BAC limit | England & Wales (80mg/100ml) / Scotland (50mg/100ml) | Road Traffic Act 1988 s.11(2); Road Traffic Act 1988 (Prescribed Limit) (Scotland) Regulations 2014 |
| Motorway speed limit | UK (70mph) / Germany (no general limit, advisory 130km/h) | Road Traffic Regulation Act 1984; StVO, Richtgeschwindigkeit since 1978 |
| Minimum driving-licence age | UK (17) / Germany (18) | Road Traffic Act 1988 (DVLA); Fahrerlaubnis-Verordnung |
| Marriage age without consent | England & Wales (18) / Scotland (16) | Marriage and Civil Partnership (Minimum Age) Act 2022 (in force 27 Feb 2023); Marriage (Scotland) Act 1977 s.1 |

Two of these facts (BAC limit, marriage age) are deliberately within-UK
jurisdictional contrasts (England & Wales vs. Scotland) rather than
UK-vs-other-country — a genuinely different, arguably harder case for the
unspecified-jurisdiction variant, since "the UK" does not have one single
answer to point to even as a folk-default. This is intentional variety,
not an error.

All 10 facts have been added to the Ethics Register (`docs/
STUDY_PROTOCOL.md` 11.4, per Protocol 5.5's requirement for every Set B
item) and signed off by the study owner (hejroe, 2026-09-09) — the same
treatment as the existing alcohol-age item.

## Provenance — Set C (10 facts, sourced 2026-09-09)

Each fact has a clean single-variable change with a specific commencement
date, drawn from a primary or authoritative source:

| Fact | Change | Effective date | Source |
|---|---|---|---|
| UK Corporation Tax main rate | 19% -> 25% (profits > GBP 250k) | 2023-04-01 | GOV.UK |
| E&W marriage age (16-year-old) | Lawful with parental consent -> not lawful at any age below 18 | 2023-02-27 | Marriage and Civil Partnership (Minimum Age) Act 2022 |
| UK standard VAT rate | 17.5% -> 20% | 2011-01-04 | Value Added Tax Act 1994, as amended |
| UK National Living Wage (23-year-old) | GBP 10.42 -> GBP 11.44 per hour | 2024-04-01 | GOV.UK minimum wage rate tables |
| US federal tobacco purchase age | 18 -> 21 | 2019-12-20 | Tobacco 21 law |
| E&W divorce grounds | Fault/separation grounds required -> no-fault statement sufficient | 2022-04-06 | Divorce, Dissolution and Separation Act 2020 |
| UK Soft Drinks Industry Levy | Did not exist -> applies | 2018-04-06 | Finance Act 2017, Part 2 |
| England smoking in enclosed public places | Permitted -> banned | 2007-07-01 | Health Act 2006 |
| England single-use plastic bag charge | Free -> minimum 5p charge | 2015-10-05 | The Single Use Carrier Bags Charges (England) Order 2015 |
| London Congestion Charge | Did not exist -> daily charge applies | 2003-02-17 | Greater London (Central Zone) Congestion Charging Order 2001 |

The National Living Wage fact is deliberately fixed to a single age band
(23-year-old) across both versions, even though the real-world change on
1 April 2024 also lowered the qualifying age from 23 to 21 — fixing the
age keeps the gold answer a single clean rate change rather than
conflating two variables (rate and eligibility) in one question.

## Translations (German, Swahili, Bengali) — reviewed 2026-09-11

Every non-English row in `set_b.csv` and `set_c.csv` carries
`review_status: translation-reviewed`. These translations were
machine-drafted and have since been reviewed by the study owner
(hejroe, 2026-09-11), the same review applied to Appendix A.3's
Swahili/Bengali IDK markers. `gold_answer`, `effective_from`/
`effective_until`, and `source_citation` are deliberately left
untranslated across all language variants of a fact — the same
convention already used in `set_a.csv` — since these fields serve as the
canonical reference for scoring regardless of the language a model was
queried in, and translating them repeatedly across three languages adds
translation-error surface for no scoring benefit.

## Files

| File | Rows | Notes |
|---|---|---|
| `set_a.csv` | 24 | Unchanged from v0.1 |
| `set_b.csv` | 120 | 10 facts x (1 unspecified + 2 jurisdiction variants) x 4 languages |
| `set_c.csv` | 80 | 10 facts x 2 versions x 4 languages |
| `set_e.csv` | 2 | Unchanged from v0.1; both rows `accepted` |
| `set_f.csv` | 2 | Unchanged from v0.1 |

## Still open

- Ten facts per family is enough to demonstrate the statistical methods
  running on real data — it is not full statistical power for a
  confirmatory RQ2/RQ3 claim (Protocol 12.2 already states this
  limitation, unchanged by this release).
- Set D (`tool_required`) tagging has not been extended to any Set B/C
  item in this release; it remains applied only within Set A.
