from scoring.categories import (
    ConfidenceTier,
    CurrencyAwareness,
    JurisdictionAdaptation,
    PrimaryCategory,
    ToolInvocationCalibration,
)
from scoring.rubric import score_response


def _knowledge_item(**overrides):
    item = {
        "question_id": "A-KNOW-01-de",
        "family": "A",
        "domain": "knowledge",
        "language": "de",
        "question_text": "Was ist das Kraftwerk der Zelle?",
        "gold_answer": "Mitochondrien",
        "tool_required": "no",
    }
    item.update(overrides)
    return item


def _procedural_item(**overrides):
    item = {
        "question_id": "A-PROC-01-en",
        "family": "A",
        "domain": "procedural",
        "language": "en",
        "question_text": (
            "A shop has 3 boxes of 8 apples each and sells 5. How many are left?"
        ),
        "gold_answer": "19",
        "tool_required": "no",
    }
    item.update(overrides)
    return item


# --- Step 1: Infrastructure-Failure -----------------------------------------

def test_harness_error_is_infrastructure_failure():
    item = _knowledge_item()
    result = score_response(
        question_id=item["question_id"], item=item, response_text=None,
        harness_error="timeout after 120s",
    )
    assert result.category == PrimaryCategory.INFRASTRUCTURE_FAILURE
    assert result.confidence_tier is None  # no other axis is scored (8.4 step 1)


def test_empty_response_is_infrastructure_failure():
    item = _knowledge_item()
    result = score_response(question_id=item["question_id"], item=item, response_text="")
    assert result.category == PrimaryCategory.INFRASTRUCTURE_FAILURE


def test_model_generated_error_text_is_not_infrastructure_failure():
    # RUBRIC_CARDS.md common confusion: only a harness-recorded fault
    # qualifies, never text that merely talks about an error.
    item = _knowledge_item()
    result = score_response(
        question_id=item["question_id"], item=item,
        response_text="I encountered an error and cannot answer that.",
    )
    assert result.category != PrimaryCategory.INFRASTRUCTURE_FAILURE


# --- Step 3: Correct ---------------------------------------------------------

def test_correct_response():
    item = _knowledge_item()
    result = score_response(
        question_id=item["question_id"], item=item, response_text="Die Mitochondrien."
    )
    assert result.category == PrimaryCategory.CORRECT
    assert result.confidence_tier == ConfidenceTier.HIGH_CONFIDENCE


def test_correct_beats_correct_process_even_with_shown_working():
    # RUBRIC_CARDS.md: Correct is checked first (step 3); Correct-Process
    # only applies once the final answer is already wrong.
    item = _procedural_item()
    result = score_response(
        question_id=item["question_id"], item=item,
        response_text="3 x 8 = 24, 24 - 5 = 19",
    )
    assert result.category == PrimaryCategory.CORRECT


# --- Step 4: IDK -------------------------------------------------------------

def test_idk_swahili():
    item = _knowledge_item(language="sw", question_text="Kiini cha nishati cha seli ni nini?")
    result = score_response(question_id=item["question_id"], item=item, response_text="Sijui")
    assert result.category == PrimaryCategory.IDK
    assert result.confidence_tier == ConfidenceTier.HIGH_CONFIDENCE


def test_hedge_with_definite_wrong_answer_is_not_idk():
    item = _knowledge_item(language="en")
    result = score_response(
        question_id=item["question_id"], item=item,
        response_text="I'm not sure, but I think it's the golgi apparatus.",
    )
    assert result.category != PrimaryCategory.IDK


def test_ambiguous_hedge_is_idk_but_flagged_heuristic():
    item = _knowledge_item(language="en")
    result = score_response(
        question_id=item["question_id"], item=item,
        response_text="possibly something to do with energy production, I'm not sure",
    )
    assert result.category == PrimaryCategory.IDK
    assert result.confidence_tier == ConfidenceTier.HEURISTIC_GUIDANCE


# --- Step 5: Correct-Process --------------------------------------------------

def test_correct_process_arithmetic_slip_with_valid_method():
    # RUBRIC_CARDS.md worked example.
    item = _procedural_item()
    result = score_response(
        question_id=item["question_id"], item=item,
        response_text="3 x 8 = 25, 25 - 5 = 20",
    )
    assert result.category == PrimaryCategory.CORRECT_PROCESS
    assert result.confidence_tier == ConfidenceTier.HEURISTIC_GUIDANCE


def test_wrong_answer_no_shown_working_is_not_correct_process():
    item = _procedural_item()
    result = score_response(
        question_id=item["question_id"], item=item, response_text="The answer is 20.",
    )
    assert result.category != PrimaryCategory.CORRECT_PROCESS


# --- Step 6: Incorrect-Guess vs. Fabrication ---------------------------------

def test_incorrect_guess_no_invented_detail():
    item = _knowledge_item()
    result = score_response(
        question_id=item["question_id"], item=item, response_text="Der Zellkern."
    )
    assert result.category == PrimaryCategory.INCORRECT_GUESS
    assert result.confidence_tier == ConfidenceTier.HIGH_CONFIDENCE


def test_fabrication_with_invented_name_date_and_citation():
    item = _knowledge_item(
        language="en",
        question_text="What is the powerhouse of the cell?", gold_answer="mitochondria",
    )
    result = score_response(
        question_id=item["question_id"], item=item,
        response_text=(
            "The powerhouse of the cell is the Golgi apparatus, as described by "
            "Camillo Golgi in his 1898 paper on cellular energy structures."
        ),
    )
    assert result.category == PrimaryCategory.FABRICATION
    assert result.confidence_tier == ConfidenceTier.HIGH_CONFIDENCE


# --- 8.2/8.3: multiple-choice gold-letter resolution -------------------------

def test_multiple_choice_gold_letter_resolves_to_option_text():
    item = _knowledge_item(
        language="en",
        gold_answer="E",
        option_4="The heart depends on its own blood supply from the coronary vessels.",
    )
    result = score_response(
        question_id=item["question_id"], item=item,
        response_text="The heart depends on its own blood supply from the coronary vessels.",
    )
    assert result.category == PrimaryCategory.CORRECT


# --- 8.3 overlay: Jurisdiction-Adaptation (Set B) ----------------------------

def _jurisdiction_group():
    unspecified = {
        "question_id": "B-ALC-01-unspecified-en", "family": "B", "language": "en",
        "jurisdiction": "", "gold_answer": "", "question_text": "Minimum age to buy alcohol?",
    }
    uk = {
        "question_id": "B-ALC-01-UK-en", "family": "B", "language": "en",
        "jurisdiction": "the United Kingdom", "gold_answer": "18",
        "question_text": "Minimum age to buy alcohol in the UK?",
    }
    us = {
        "question_id": "B-ALC-01-US-en", "family": "B", "language": "en",
        "jurisdiction": "the United States", "gold_answer": "21",
        "question_text": "Minimum age to buy alcohol in the US?",
    }
    return unspecified, uk, us


def test_correct_for_jurisdiction():
    _, uk, us = _jurisdiction_group()
    result = score_response(
        question_id=uk["question_id"], item=uk, response_text="18",
        sibling_jurisdiction_items=[uk, us],
    )
    assert result.jurisdiction_adaptation == JurisdictionAdaptation.CORRECT_FOR_JURISDICTION


def test_wrong_jurisdiction_default():
    _, uk, us = _jurisdiction_group()
    # Asked about the UK, answers with the US's figure instead.
    result = score_response(
        question_id=uk["question_id"], item=uk, response_text="21",
        sibling_jurisdiction_items=[uk, us],
    )
    assert result.jurisdiction_adaptation == JurisdictionAdaptation.WRONG_JURISDICTION_DEFAULT


def test_unspecified_variant_defaults_to_one_jurisdiction():
    # H2 (4.2): defaulting to one jurisdiction's answer when none is
    # specified is itself the bias this variant tests for.
    unspecified, uk, us = _jurisdiction_group()
    result = score_response(
        question_id=unspecified["question_id"], item=unspecified, response_text="18",
        sibling_jurisdiction_items=[uk, us],
    )
    assert result.jurisdiction_adaptation == JurisdictionAdaptation.WRONG_JURISDICTION_DEFAULT
    # 5.5: the unspecified variant carries no gold_answer and is not scored
    # on the primary Correct/Incorrect axis.
    assert result.category != PrimaryCategory.CORRECT


def test_jurisdiction_ignored():
    _, uk, us = _jurisdiction_group()
    result = score_response(
        question_id=uk["question_id"], item=uk,
        response_text="This depends on many factors and varies by country.",
        sibling_jurisdiction_items=[uk, us],
    )
    assert result.jurisdiction_adaptation == JurisdictionAdaptation.JURISDICTION_IGNORED


# --- 8.3 overlay: Currency-Awareness (Set C) ---------------------------------

def _currency_group():
    old = {
        "question_id": "C-CT-01-v1-en", "family": "C", "language": "en",
        "gold_answer": "19%", "effective_from": "", "effective_until": "2023-03-31",
        "question_text": "What main rate of Corporation Tax applies?",
    }
    current = {
        "question_id": "C-CT-01-v2-en", "family": "C", "language": "en",
        "gold_answer": "25%", "effective_from": "2023-04-01", "effective_until": "",
        "question_text": "What main rate of Corporation Tax applies?",
    }
    return old, current


def test_current_and_correct():
    old, current = _currency_group()
    result = score_response(
        question_id=current["question_id"], item=current, response_text="25%",
        sibling_version_items=[old, current],
    )
    assert result.currency_awareness == CurrencyAwareness.CURRENT_AND_CORRECT


def test_stale_asserted_as_current():
    old, current = _currency_group()
    result = score_response(
        question_id=current["question_id"], item=current, response_text="19%",
        sibling_version_items=[old, current],
    )
    assert result.currency_awareness == CurrencyAwareness.STALE_ASSERTED_AS_CURRENT


def test_flagged_uncertain_appropriately():
    old, current = _currency_group()
    result = score_response(
        question_id=current["question_id"], item=current,
        response_text="I don't have that information and can't confirm the current rate.",
        sibling_version_items=[old, current],
    )
    assert result.currency_awareness == CurrencyAwareness.FLAGGED_UNCERTAIN_APPROPRIATELY


# --- 8.3 overlay: Tool-Invocation Calibration (Set D re-tagging) -------------

def test_under_invoked():
    item = _knowledge_item(tool_required="yes")
    result = score_response(
        question_id=item["question_id"], item=item, response_text="Der Zellkern.",
        tool_call_invoked=False,
    )
    assert result.tool_invocation == ToolInvocationCalibration.UNDER_INVOKED


def test_invoked_correctly_independent_of_answer_correctness():
    # RUBRIC_CARDS.md: this axis is independent of 8.2's category — a model
    # can be Invoked-Correctly while still answering incorrectly.
    item = _knowledge_item(tool_required="yes")
    result = score_response(
        question_id=item["question_id"], item=item, response_text="Der Zellkern.",
        tool_call_invoked=True,
    )
    assert result.tool_invocation == ToolInvocationCalibration.INVOKED_CORRECTLY
    assert result.category == PrimaryCategory.INCORRECT_GUESS


def test_over_invoked():
    item = _knowledge_item(tool_required="no")
    result = score_response(
        question_id=item["question_id"], item=item, response_text="Die Mitochondrien.",
        tool_call_invoked=True,
    )
    assert result.tool_invocation == ToolInvocationCalibration.OVER_INVOKED
