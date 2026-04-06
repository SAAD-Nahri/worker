# Phase 2 Acceptance Batch 7

## Purpose

This acceptance note resolves the last open closeout question from Batch 6:

Does the fixed gold set still need one more clean-fit expansion before Phase 2 can close?

## Audit Method

Instead of forcing a new clean-fit case into the pack, the remaining live unique source items were replayed through the real deterministic formatter and routing layer.

The goal was to classify the remaining uncovered candidates honestly:

1. true clean-fit additions,
2. weak-fit families that should be routed out,
3. non-representative noise that should not shape the closeout pack.

## What The Audit Found

Two remaining live `pass` plus `proceed` candidates were not actually trustworthy clean-fit additions.

### 1. Haunted restaurant novelty story

Source item:

`This NYC Restaurant Is Supposedly Haunted By Over 20 Ghosts`

Audit finding:

1. the formatter can still produce a structurally valid draft,
2. but the content is venue-novelty coverage, not a good short food explainer fit,
3. allowing it to proceed would create false confidence in the current template set.

Decision:

1. add this family to weak-fit routing,
2. add it to the gold set as a `hold_for_reroute` case,
3. do not treat it as the missing clean-fit expansion.

### 2. Big Arch state-by-state price comparison story

Source item:

`The US States With The Most And Least Expensive McDonald's Big Arch Burger`

Audit finding:

1. the formatter can still produce a draft,
2. but the story is a geographic price-comparison roundup,
3. it is better modeled as comparison content than as a clean explainer.

Decision:

1. add this family to weak-fit routing,
2. add it to the gold set as a `hold_for_reroute` case,
3. do not treat it as the missing clean-fit expansion.

## Strategic Decision

The current gold set does **not** need a forced extra clean-fit case from the present live source pool.

The more honest conclusion is:

1. the existing clean-fit set is already representative enough for the current template families,
2. the remaining uncovered live candidates were actually exposing weak-fit routing gaps,
3. closing those gaps is better than padding the pack with a fake "clean" addition.

## Changes Made

The repo baseline now includes two new fixed cases:

1. `haunted_restaurant_novelty_hold`
2. `big_arch_price_comparison_hold`

The weak-fit routing layer now also explicitly covers:

1. venue-novelty restaurant stories,
2. geographic price-comparison roundups.

## Validation

Focused validation:

```powershell
python -m unittest tests.unit.content_engine.test_routing -v
```

Full validation:

```powershell
python -m unittest discover -s tests -v
python src\cli\replay_phase2_gold_set.py
```

## Result

This batch resolves the last substantive Phase 2 closeout decision.

The fixed pack is now strong enough to freeze without pretending the current live source pool contains more clean-fit variety than it really does.

The correct next step after this batch is the formal Phase 2 closeout review.
