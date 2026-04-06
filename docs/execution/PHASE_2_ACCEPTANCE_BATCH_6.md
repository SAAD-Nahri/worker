# Phase 2 Acceptance Batch 6

## Purpose

This replay checks the bounded headline-variant slice after tightening the heuristic provider.

The goal is not to make headline generation "smart."

The goal is to make it safe enough that:

1. title-shape handling is no longer obviously awkward,
2. weak wrappers are discarded instead of preserved,
3. the draft record keeps useful review aids without pretending they are final titles.

## Why This Replay Was Needed

The earlier Phase 2 baseline proved that draft creation, quality gates, routing, and review mechanics were working.

It also exposed one narrow but real weakness:

1. heuristic headline variants could drift into awkward wrappers like `Why To ...`,
2. generic endings like `Matters In The Kitchen` were too broad to trust,
3. provider output needed stronger filtering before it was written back into the draft record.

That did not justify widening AI scope.

It justified tightening the bounded micro-skill contract.

## What Changed

The current code baseline now:

1. generates headline variants with title-shape-aware heuristics,
2. reuses source-title subject handling instead of wrapping every title the same way,
3. rejects clicky or awkward variants before they reach the draft record,
4. falls back to safer deterministic variants when provider output is too weak.

## Representative Replay Cases

### 1. Why-style title

Source title:

`Why This Kitchen Trick Works`

Current heuristic variants:

1. `What Makes This Kitchen Trick Work`
2. `The Pattern Behind This Kitchen Trick`
3. `A Clearer Look At This Kitchen Trick`

### 2. How-to second-life title

Source title:

`How To Give Your Costco Croissant Container A Second Life`

Current heuristic variants:

1. `Why Your Costco Croissant Container Is Worth Saving`
2. `A Better Second Use For Your Costco Croissant Container`
3. `How Your Costco Croissant Container Can Be Reused`

### 3. List-style avoidance title

Source title:

`The Only 2 Foods Jacques Pepin Thinks Twice About Eating`

Current heuristic variants:

1. `Which Foods Jacques Pepin Avoids`
2. `Why Jacques Pepin Still Skips Certain Foods`
3. `A Clearer Look At The Foods Jacques Pepin Avoids`

## Validation

Focused validation:

```powershell
python -m unittest tests.unit.content_engine.test_micro_skills -v
python -m unittest tests.unit.content_engine.test_micro_skill_cli -v
```

Full regression validation:

```powershell
python -m unittest discover -s tests -v
python src\cli\replay_phase2_gold_set.py
```

## Result

This replay closes the earlier headline-quality gap enough for Phase 2 closeout planning.

The important result is not that headline heuristics are now "final quality."

The important result is:

1. heuristic headline suggestions are now conservative enough to keep as review aids,
2. obviously awkward wrapper patterns are filtered out,
3. the system no longer needs to treat weak heuristic headline output as a Phase 2 blocker by itself.

## Remaining Rule

Headline variants remain optional review support.

They are not a reason to bypass:

1. title honesty review,
2. manual title selection,
3. later title refinement in Phase 3 or beyond.
