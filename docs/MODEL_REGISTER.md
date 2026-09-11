# Model Register

**Status:** DRAFT
**Version:** 0.2 (versions with the model set, per Protocol 7.5/5.8)
**Companion to:** `STUDY_PROTOCOL.md` Section 7 (7.2 references this document by
name as the licence-vetting record; 7.3's Candidate Models table is the
Protocol's own summary — this Register is the fuller governance record,
following the same discipline as the Source Register (5.4) and Ethics
Register (11.4): every candidate logged, included or excluded, with the
checks performed and the reasoning behind the decision.

## Purpose

Section 7.2 requires every candidate model to be licence-vetted —
ownership/provenance, licence compatibility, and currency — before use,
"per the Model Register (a separate governance document)." This is that
document. It does not restate 7.1-7.5's selection criteria or rationale;
it records the vetting outcome for each candidate, and is the
authoritative place a status is marked Confirmed once reviewed.

## Register

| Model | Vendor / Ownership check | Licence (as stated) | Licence confirmation status | Deployment evidence | Currency check | Decision | Reasoning |
|---|---|---|---|---|---|---|---|
| Llama 3.2 1B | Meta — clear, well-known vendor | Llama 3.2 Community Licence (conditions apply, incl. >700M MAU clause) | Confirmed — licence text is public and unambiguous for this use | Most widely deployed open-model family; casual-deployment baseline | Actively maintained | Included | Meets 7.2's vendor-diversity and real-world-deployment criteria; edge tier |
| SmolLM2-1.7B | Hugging Face — clear, well-known vendor | Apache-2.0 | Confirmed — permissive, unconditional | Purpose-built small model, actively maintained | Actively maintained | Included | Clear licence, no share-alike or MAU conditions; edge tier, general-purpose contrast |
| Gemma 3n (E2B) | Google — clear, well-known vendor | Custom Gemma Terms; commercial use permitted, subject to a Prohibited-Use Policy | Confirmed — Prohibited-Use Policy reviewed in full by the study owner and permits this use (hejroe, 2026-09-11) | Google's own edge-architected model line | Actively maintained | Included | Meets 7.2's edge-tier criteria; licence confirmed |
| Qwen3-1.7B | Alibaba — clear, well-known vendor | Reported Apache-2.0 across the Qwen3 family | Confirmed — Apache-2.0 for this specific checkpoint, reviewed by the study owner (hejroe, 2026-09-11) | Included as the multilingual-optimised contrast, not the anchor of the set | Actively maintained | Included | Clear licence; multilingual-optimised contrast |
| Llama 3.2 3B | Meta — clear, well-known vendor | Llama 3.2 Community Licence | Confirmed — same licence text as the 1B variant | Same casual-deployment rationale as the 1B | Actively maintained | Included | Small tier general-purpose contrast |
| Phi-4-mini | Microsoft — clear, well-known vendor | MIT | Confirmed — from the model card directly | Confirmed popular via an independent Ollama-usage ranking, not a curated list | Actively maintained | Included | Clear licence, no conditions; small tier, general-purpose |
| Qwen3 4B | Alibaba — clear, well-known vendor | Reported Apache-2.0 | Confirmed — Apache-2.0 for this specific checkpoint, reviewed by the study owner (hejroe, 2026-09-11) | Multilingual-optimised contrast at this size tier | Actively maintained | Included | Clear licence; multilingual-optimised contrast at this size tier |
| TinyLlama 1.1B | — not vetted | — not vetted | N/A | — | Superseded — a 2023/24-era model now measurably behind SmolLM2 and Qwen3 at the same size on current benchmarks | Excluded | Superseded; licence vetting not performed since the model was excluded on merit before reaching this stage |
| Mistral (7B and above) | — not vetted | — not vetted | N/A | — | — | Excluded | No genuine sub-4B variant exists; does not fit either size tier defined in 7.2 |
| Llama 3.1 8B, Qwen3-8B, GLM-4-9B | — not vetted | — not vetted | N/A | — | — | Excluded | Frequently mislabelled "edge" in public sources; real models, but outside the size band this study tests |

*Licence readings above are a preliminary technical check, not legal
advice (12.7); every "Confirmed" status reflects a direct reading of the
publicly stated licence text, not an independent legal opinion, and every
"Included" decision still requires that confirmation before the model is
relied on for reportable results or commercial use.*

## Licence Confirmations (Resolved 2026-09-11)

Two licence details were flagged as open in the Protocol (7.5, 12.5) and
are now resolved:

1. **Qwen3's exact per-size licence terms** — Apache-2.0 is reported
   across the Qwen3 family; the study owner has reviewed and confirmed it
   for the specific 1.7B and 4B checkpoints used here.
2. **Gemma 3n's Prohibited-Use Policy**, in full — reviewed end to end by
   the study owner, who confirms it permits this use.

This Register — not Section 7.3, and not the Protocol's own text — is the
authoritative place that resolution is recorded.

## Versioning

This Register versions with the model set (Protocol 7.5, corpus-aligned
per 5.8): adding a new candidate, revisiting an excluded one, or resolving
a Pending confirmation is a Register update, not a Protocol edit — the
Protocol's own tables (7.3, 7.4) only need to change if the *set itself*
changes, not when a confirmation status here is resolved.
