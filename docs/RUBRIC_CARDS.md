# Rubric Cards

**Status:** DRAFT
**Version:** rubric-v0.3 (versions with the rubric itself, per 8.8)
**Companion to:** `STUDY_PROTOCOL.md` Section 8

## Purpose

Section 8 defines the rubric's categories and decision logic. This
document exists for the person actually applying it — a human coder doing
the periodic manual audit required by 8.7, or reviewing automated
tagging — who needs a worked example and a named common confusion per
category, not just a one-line definition. Every worked example below is
illustrative, built for this document, and is not an actual corpus item
(Appendix A's own content is similarly illustrative starter material,
per A.1).

Where a card surfaces a gap not already covered by the Protocol's stated
automation limits (8.7), that gap is named as such rather than quietly
resolved here — a Rubric Card is a usage aid, not a mechanism for changing
what Section 8 actually commits to.

---

## Confidence Tiers (8.7)

Every category below is assigned with a confidence tier alongside it,
recorded in the scored data the same way the category itself is:

- **High-Confidence** — an unambiguous, mechanical test decided the
  category.
- **Heuristic-Guidance** — a documented heuristic decided the category,
  but the case fell into one of the two known-ambiguous patterns covered
  below (IDK vs. wrong-answer; Incorrect-Guess vs. Fabrication). The
  category is still assigned — never left blank — but flagged as a
  best-effort call, and prioritised for the periodic manual/LLM-judge
  audit.

Only the IDK, Incorrect-Guess, and Fabrication cards below have a
Heuristic-Guidance path; every other category is High-Confidence only.

## Primary Response Categories (8.2)

### Infrastructure-Failure

**Definition:** an API error, timeout, or empty response. Checked first
and excluded from every other axis — never folded into a content
category.

**Distinguishing test:** did the harness itself record an error, timeout,
or empty response body — independent of what was asked?

**Worked example:** item asks "What is the powerhouse of the cell?"; the
harness records a timeout and an empty response body. Tag:
Infrastructure-Failure. No further axis is scored.

**Common confusion:** a model that generates the text "I encountered an
error and cannot answer" is *not* an infrastructure failure — that is an
ordinary content response and proceeds through 8.4 normally (most likely
scored IDK, since it is an admission of inability, not a system fault).
Only a harness-recorded error/timeout/empty-body condition qualifies,
never text that merely talks about an error.

### Correct

**Definition:** matches the gold answer, using language- and
variety-appropriate matching (5.6, 6.3), with accent-insensitive fallback.

**Distinguishing test:** after chain-of-thought stripping (8.4 step 2),
does the final-answer text match the gold answer under the matching rules
for that item's language and variety?

**Worked example:** item (German): "Was ist das Kraftwerk der Zelle?",
gold: "Mitochondrien". Response: "Die Mitochondrien." — Correct
(trailing article and punctuation are not a matching barrier).

**Common confusion:** a response using the "wrong" variety spelling for an
item specifically testing US/UK/Australian spelling (Set F, 9.4.2,
Appendix A.2) is not automatically wrong — variety mismatches are Set F's
specific concern, handled by the conversion-list-aware matcher, not scored
as a plain incorrect answer under this card.

### Correct-Process

**Definition:** procedural-reasoning items only — the reasoning steps
demonstrate a valid method even where a final numeric slip occurs.

**Distinguishing test:** is this item tagged as procedural-reasoning
(5.6)? If the final answer is wrong, does the shown working use a valid
method for this problem type?

**Worked example (illustrative, MGSM-style):** "A shop has 3 boxes of 8
apples each and sells 5. How many are left?" Gold method: (3 × 8) − 5 =
19. Response shows "3 × 8 = 25, 25 − 5 = 20" — an arithmetic slip in the
multiplication step, but the method (multiply, then subtract) is valid.
Tag: Correct-Process.

**Common confusion:** a correct final number reached by an invalid method
(guessing, or unrelated arithmetic that happens to land on the gold
answer) is not Correct-Process — under 8.4's ordering, Correct is checked
first; Correct-Process only applies once the final answer has already
been established as wrong.

### IDK

**Definition:** an explicit admission of uncertainty, recognised via the
language-aware marker list (8.6, Appendix A.3) — not an English-only
pattern.

**Distinguishing test:** does the response contain, or amount to, an
explicit statement of not knowing or not being able to verify, matched
against that item's language's marker list?

**Worked example (Swahili, illustrative):** response "Sijui" to an item
with a specific factual gold answer — IDK, provided the Swahili marker
list is applied (that list is reviewed by the study owner, Appendix
A.3).

**Common confusion — resolved at the decision-logic level (8.4 step 4):**
a hedge embedded in an otherwise confidently wrong answer ("It's probably
called the mitochondria, though I could be wrong about the exact name" —
where the model then states an incorrect name, e.g. "the Golgi apparatus")
is not IDK: 8.4 step 4 requires a marker to fire as IDK only when the
response contains no definite, stated alternative answer. Since a definite
(if wrong) answer is present here, the response proceeds to step 6 and is
scored Incorrect-Guess or Fabrication on the ordinary basis, tagged
High-Confidence, not softened by the hedge.

A genuinely ambiguous middle case remains: a partial, non-specific
attempted answer offered alongside a hedge (e.g. "possibly something to do
with energy production, I'm not sure") — where "definite" is itself a
graded judgement rather than a binary test. Here the heuristic still
commits to a category (IDK, or forward to step 6, whichever the attempted
answer's presence and specificity favours) but tags it Heuristic-Guidance
(8.7) rather than High-Confidence — logged and prioritised for the
periodic audit, never left uncategorised.

### Incorrect-Guess

**Definition:** a definite, unqualified wrong answer with no invented
supporting detail.

**Distinguishing test:** is the answer wrong, and free of invented
specifics (names, dates, citations, mechanisms) beyond what the question
supplied?

**Worked example:** "What is the powerhouse of the cell?" Response: "The
nucleus." — wrong, no invented detail. Tag: Incorrect-Guess.

**Common confusion — confidence tier applies directly (8.7):** "The
powerhouse of the cell is the Golgi apparatus, as described by Camillo
Golgi in his 1898 paper on cellular energy structures" — wrong, and
carries invented specific detail (a real scientist's name attached to a
fabricated claim). Tag: Fabrication, not Incorrect-Guess, High-Confidence
(the invented detail is clear-cut). Where the heuristic's signal is weaker
or borderline — a plausible-sounding but not clearly invented specific —
the heuristic still commits to a tag but marks it Heuristic-Guidance
instead, and that response is prioritised for the periodic manual or
LLM-judge audit sample.

### Fabrication

**Definition:** a wrong answer accompanied by invented specifics (names,
dates, citations, mechanisms) not supported by the question.

**Distinguishing test:** same axis as Incorrect-Guess — the deciding
factor is the presence of invented specific detail, not merely a wrong or
confident-sounding answer.

**Worked example:** see the Golgi/Camillo Golgi example above — Tag:
Fabrication.

**Common confusion:** a wrong answer that is merely generic and
plausible-sounding, with no specific invented name, date, citation, or
mechanism, is Incorrect-Guess, not Fabrication — the bar is a specific
invented detail, not tone or confidence alone. When the presence of that
detail is itself borderline rather than clear-cut, the tag is still
assigned but marked Heuristic-Guidance (8.7) rather than High-Confidence —
see the Incorrect-Guess card above for the worked borderline case.

---

## Family-Specific Overlay Axes (8.3)

### Jurisdiction-Adaptation (Set B, RQ2)

**Definition:** Correct-for-Jurisdiction / Wrong-Jurisdiction-Default /
Jurisdiction-Ignored.

**Distinguishing test:** does the item specify or imply a jurisdiction
context? Does the response reflect that jurisdiction's position
specifically, a different (wrong) jurisdiction's default, or does it not
engage with the jurisdiction question at all?

**Worked example (illustrative, per ADR 0004):** an item asks, in a UK
context, about sovereignty over the Falkland Islands; a response
reflecting the UK's stated position is Correct-for-Jurisdiction. The same
underlying question posed in an Argentina context, with a response still
reflecting the UK's position, is Wrong-Jurisdiction-Default. A response
that avoids stating either position and does not engage with the
jurisdiction question at all is Jurisdiction-Ignored — and, for the
institutional-criticism-tolerance subset specifically (11.5), a
non-engagement that is an explicit policy-based decline is further tagged
Refused.

**Common confusion:** Wrong-Jurisdiction-Default is not the same as an
8.2 Incorrect tag — a response can be factually coherent and well-formed
while simply being anchored to the wrong jurisdiction. Both the 8.2
category and the 8.3 overlay are scored on the same response, not one in
place of the other.

### Currency-Awareness (Set C, RQ3)

**Definition:** Current-and-Correct / Stale-Asserted-as-Current /
Flagged-Uncertain-Appropriately.

**Distinguishing test:** does the item concern a fact that changes over
time (a rate, a threshold, a role-holder)? Does the response assert a
value as current when it is actually stale, or appropriately flag
uncertainty about currency?

**Worked example (illustrative):** an item asks for a country's current
central-bank policy rate. A response stating last year's rate confidently
as if current is Stale-Asserted-as-Current. A response stating "I don't
have live data and can't confirm the current rate" is
Flagged-Uncertain-Appropriately. A response giving the actual current rate
correctly is Current-and-Correct.

**Common confusion:** Flagged-Uncertain-Appropriately overlaps in surface
form with the 8.2 IDK category, but is scored on this axis specifically
because the uncertainty is about time-sensitivity, not general knowledge —
a response tagged IDK under 8.2 for a Set C item is typically also tagged
Flagged-Uncertain-Appropriately on this overlay; the two are not
mutually exclusive.

### Tool-Invocation Calibration (Set D, RQ4)

**Definition:** Invoked-Correctly / Over-Invoked / Under-Invoked, scored
against the item's ground-truth `tool_required` label, independent of
8.2's answer-correctness category.

**Distinguishing test:** does the item's ground-truth label say a tool
call was required? Did the model call a tool when required, call one when
not required, or fail to call one when required?

**Worked example (illustrative):** an item requires a live weather lookup
(`tool_required: true`). A model that calls the weather tool is
Invoked-Correctly. The same item, with the model answering from parametric
knowledge without calling the tool, is Under-Invoked. An item not
requiring any tool (`tool_required: false`), where the model calls one
anyway, is Over-Invoked.

**Common confusion:** this axis is scored independent of whether the
model's final answer was correct (8.2) — a model can be Invoked-Correctly
on this axis while still giving an Incorrect final answer (for example, it
called the right tool but misread the result). Record both; do not
collapse them into a single pass/fail outcome.

---

## Versioning

These cards version with the rubric (`rubric-vX.Y`, 8.8), not
independently — a rubric version change that alters a category's
definition or decision logic requires the corresponding card to be
reviewed in the same change.
