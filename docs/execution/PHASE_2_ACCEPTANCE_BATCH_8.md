# Phase 2 Acceptance Batch 8

## Purpose

This acceptance note records the template-contract hardening pass completed after the formal Phase 2 closeout baseline was first written.

The goal of this batch was simple:

1. make the most important template rules executable in code,
2. prove the deterministic formatter still produces compliant baseline drafts,
3. keep the Phase 2 foundation honest before Phase 3 begins.

## Why This Batch Was Needed

The earlier Phase 2 baseline already had real template contracts, but some of the strongest rules still lived mostly in prose:

1. slot-level section length expectations,
2. bullet-count expectations for bullet-driven sections,
3. early-answer placement for the food-fact template.

That gap was acceptable for initial closeout, but it was still worth hardening before later phases build on the Content Engine.

## Hardening Scope

This batch added:

1. slot-level guidance to the application-level template contracts,
2. slot-level quality checks for intro and body section soft ranges,
3. bullet-count checks for `supporting_points` and `practical_points`,
4. early-answer placement checks for `direct_answer`,
5. formatter tuning so the baseline deterministic drafts still satisfy the stronger contracts.

## Validation Commands

```powershell
python -m unittest tests.unit.content_engine.test_templates tests.unit.content_engine.test_formatting tests.unit.content_engine.test_quality -v
python -m unittest discover -s tests -v
python src\cli\replay_phase2_gold_set.py
```

## Results

1. focused template, formatting, and quality tests passed with `23/23`,
2. full unittest discovery passed with `89` tests,
3. the fixed Phase 2 gold set still passed with `14/14`,
4. one weak-fit listicle hold case was reclassified from `review_flag` to `pass + hold_for_reroute`, which is a cleaner expression of the current routing-vs-quality boundary,
5. no live runtime draft or source data needed to be modified for this hardening pass.

## What This Batch Proves

1. template IDs are no longer just labels attached to a draft shape,
2. the accepted v1 templates now carry executable slot-level constraints,
3. the deterministic formatter can still produce baseline-compliant drafts for the current accepted template families,
4. slot-level drift now appears as named review flags instead of staying hidden until manual review.

## Conclusion

Phase 2 remains closed, but this batch materially strengthens the accepted baseline.

The template layer is now a firmer foundation for later social packaging and publishing work because downstream phases can depend on:

1. stable template identity,
2. explicit section order,
3. executable slot-level guidance,
4. visible template-contract failures when a draft drifts.
