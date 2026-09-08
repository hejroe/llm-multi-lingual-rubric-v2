# 0002. Statistical test selection for paired small-sample comparisons

**Status:** Accepted
**Date:** 2026-09-08

## Context

Pilot-scale samples (5.1) are small and paired: the same items are run
against multiple models and conditions. Standard large-sample tests
(chi-square, unpaired t-tests) are a poor fit here and risk both false
precision and violated assumptions.

## Decision

Use McNemar's exact test for two-condition paired binary comparisons,
Cochran's Q test for three-way paired comparisons across models or
conditions, and Clopper-Pearson exact confidence intervals for reporting
proportions, rather than normal-approximation intervals. Multiple
comparisons are split into a pre-registered primary set (Holm-Bonferroni
corrected) and a secondary/exploratory set (uncorrected, explicitly
labelled as such) per 10.5, rather than correcting everything uniformly or
correcting nothing.

## Consequences

Statistical power at pilot scale is limited, and this is stated as a
limitation (12) rather than a solved problem. The primary/secondary split
must be frozen before data collection (4.4) to remain meaningful — moving
a result from secondary to primary after seeing the data would be a
defensibility failure, not a routine analysis choice.
