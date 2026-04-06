# Phase 2 Acceptance Batch 4

## Purpose

This acceptance note records the first closeout-oriented expansion of the fixed Phase 2 gold set.

The goal of this batch was not to generate more routine drafts.

The goal was to widen the gold set with additional live weak-fit cases so Phase 2 closeout is based on broader evidence than the original baseline pack.

## Why This Batch Was Needed

After [PHASE_2_ACCEPTANCE_BATCH_3.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_3.md), the main remaining closeout gap was clear:

1. routing was visible,
2. the original gold set was stable,
3. but the pack still needed more live weak-fit coverage before closeout.

This batch addresses that gap directly.

## Audit Scope

The remaining live source items not yet represented in the gold set were replayed through the deterministic formatter and routing layer.

That audit produced two strong new weak-fit additions:

1. `17 Recipes to Help You Survive Tax Day`
2. `Maryland Half-and-Half Crab Soup`

These cases were added because they widen coverage in meaningful ways:

1. event-driven recipe roundup behavior,
2. recipe-heavy regional soup behavior with noisy credit text in the source summary,
3. additional `hold_for_reroute` evidence from real runtime source items.

## Strategic Adjustment During The Batch

This batch also exposed a small but real deterministic issue:

1. internal hyphens in food titles were being split too aggressively,
2. that caused `Half-and-Half` titles to degrade into weaker subject anchors.

The formatter was corrected so title splitting now prefers dash clauses with surrounding spaces instead of breaking every hyphenated food phrase.

The summary cleaner was also tightened so `Props:` credit text does not leak into intro-term selection.

These are Phase 2 foundation fixes, not cosmetic polish.

## Commands Run

```powershell
python -m unittest discover -s tests -v
python src\cli\replay_phase2_gold_set.py
python src\cli\replay_phase2_gold_set.py --json
```

## Gold-Set Expansion Result

The fixed pack now includes `11` cases instead of `9`.

New live additions:

1. `tax_day_recipes_listicle_hold`
2. `maryland_crab_soup_recipe_heavy_hold`

The replay passed after expansion.

Observed result:

1. `11/11` cases passed,
2. the new live cases both routed to `hold_for_reroute`,
3. the short-ribs recipe-title case stayed stable after the title-anchor improvement,
4. the blocked synthetic control still protects the eligibility floor.

## What Improved

### 1. Live weak-fit coverage is broader

The gold set no longer relies only on one or two recipe-heavy hold patterns.

It now covers:

1. direct recipe-title pages,
2. regional soup recipe pages,
3. numbered roundup pages,
4. event-driven recipe roundup pages,
5. dashed consumer-news titles.

### 2. Title handling is safer

`Maryland Half-and-Half Crab Soup` now preserves the full food title instead of collapsing to a weaker partial anchor.

### 3. Credit noise is less likely to leak into intros

The Maryland case now protects against `Jono Pandolfi` and other summary-credit noise re-entering the intro-term path.

## What Still Does Not Close Phase 2

This batch improves closeout readiness, but it does not fully close Phase 2.

The biggest remaining gap is still:

1. at least one live blocked case is still missing from the fixed gold set.

That means the synthetic blocked control is still necessary, but no longer sufficient as the only blocked representation.

## Conclusion

Batch 4 is a real closeout-grade improvement.

It does not just add more examples. It adds better evidence:

1. more live weak-fit coverage,
2. a cleaner title-anchor rule,
3. a stronger fixed replay baseline for the next Phase 2 quality changes.
