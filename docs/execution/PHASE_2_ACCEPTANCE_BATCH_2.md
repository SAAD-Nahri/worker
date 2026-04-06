# Phase 2 Acceptance Batch 2

## Purpose

This document records the second live-style Phase 2 acceptance pass after the semantic-anchor and content-fit improvements were implemented.

This was not a new publishing batch.

It was a controlled replay of the same four real source items used in [PHASE_2_ACCEPTANCE_BATCH_1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_1.md) so the repo could measure whether the deterministic quality work actually improved the draft foundation.

## What Changed Before This Replay

The repo gained four important deterministic improvements:

1. candidate-paragraph filtering now removes more boilerplate, attribution noise, and procedural recipe text,
2. topic-term extraction now relies more on title and cleaned body support and less on raw summary fragments,
3. content-fit signals are now recorded through semantic-profile checks,
4. quality gates now review-flag recipe-heavy and noisy source context instead of letting those cases pass silently.

These changes were guided by the first live batch and the new [CONTENT_FIT_GATE_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/CONTENT_FIT_GATE_V1.md) spec.

## Replay Scope

The replay used the same live `source_item_id` values:

1. `b3b1fae29b000493955232a2574e3317f0c8e375`
2. `5d1d078eb1ee712d2d76cd96a5578e47b9cf7543`
3. `0637ac87046ef3cc65bc45e52155c9f627622329`
4. `c421b428894b627aa30123361debffe193871270`

The replay was performed in-process by formatting those source items directly without appending new runtime draft snapshots.

## Validation Commands

```powershell
python -m unittest discover -s tests -v
```

Live-style replay command used:

```powershell
@'
import sys
sys.path.insert(0, r'.\src')
from content_engine.formatting import format_source_item_to_draft
from source_engine.storage import read_source_items

ids = [
    'b3b1fae29b000493955232a2574e3317f0c8e375',
    '5d1d078eb1ee712d2d76cd96a5578e47b9cf7543',
    '0637ac87046ef3cc65bc45e52155c9f627622329',
    'c421b428894b627aa30123361debffe193871270',
]
items = {item.item_id: item for item in read_source_items()}

for item_id in ids:
    draft = format_source_item_to_draft(items[item_id], created_at='2026-04-03T03:15:00+00:00')
    print(item_id, draft.quality_gate_status, draft.quality_flags, draft.intro_text)
'@ | python -
```

## Replay Results

| source_item_id | raw_title | quality result | key intro improvement |
|---|---|---|---|
| `b3b1fae29b000493955232a2574e3317f0c8e375` | `Pak Mo Krob (Thai Vietnamese Crispy Rice Paper Wrap)` | `pass` | Subject now anchors on `Thai Vietnamese Crispy Rice Paper Wrap` instead of filler-like fragments. |
| `5d1d078eb1ee712d2d76cd96a5578e47b9cf7543` | `Tsoureki (Greek Easter Bread)` | `review_flag` | The draft now surfaces a clean subject while explicitly flagging recipe-heavy and noisy source context. |
| `0637ac87046ef3cc65bc45e52155c9f627622329` | `How To Give Your Costco Croissant Container A Second Life` | `pass` | The intro now frames the piece around `second life` and `environmental sustainability` instead of placeholder-like term fragments. |
| `c421b428894b627aa30123361debffe193871270` | `The Only 2 Foods Jacques Pépin Thinks Twice About Eating` | `pass` | The intro now names `coconut` and `marshmallows` instead of weak summary fragments. |

## Comparison To Batch 1

### Improvements

1. The Jacques Pépin item no longer uses summary junk like `exceptions prove he'll`.
2. The Costco container item no longer uses placeholder-like support phrasing.
3. The Tsoureki item is now explicitly surfaced as a weak-fit explainer source instead of quietly passing.
4. Boilerplate and procedural recipe text now influence the draft much less than they did in the first batch.

### Remaining Weaknesses

1. The Pak Mo Krob item is usable, but the support-anchor wording is still only serviceable, not polished.
2. Some foreign-dish and culture-heavy recipe pages still require stronger routing or richer explainer framing than the current deterministic path provides.
3. The current heuristic micro-skill layer still has not solved headline quality and should remain secondary to deterministic quality improvements.

## Most Important Findings

### 1. The strategic change was correct

Treating anchor quality and content-fit as explicit deterministic concerns improved the real outputs immediately.

### 2. Not all "passes" are equal

The replay shows cleaner passes than Batch 1, but some `pass` outcomes still represent drafts that are structurally safe more than editorially strong.

That is acceptable for the current stage as long as:

1. review remains active,
2. the gold-set closeout gate is added,
3. weak-fit families are not silently scaled.

### 3. Recipe-heavy context should remain visible

The Tsoureki result is a good example of professional behavior:

1. the draft is no longer semantically confused,
2. the system still does not pretend the source is a clean automatic pass,
3. review is still required.

## What This Means For Phase 2

Phase 2 is stronger than it was after Batch 1, but it is still not closeout-ready.

The next highest-value steps are:

1. build the fixed gold-set acceptance pack for semantic-anchor validation,
2. decide which weak-fit source families should be rerouted or rejected before full draft emission,
3. continue improving bounded headline quality only after the gold set exists.

## Conclusion

Batch 2 is a real foundation improvement.

It shows that the repo is no longer only identifying the semantic problem. It is now correcting part of it deterministically and documenting the remaining gap honestly.
