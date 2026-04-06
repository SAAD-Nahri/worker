# Phase 2 Acceptance Batch 1

## Purpose

This document records the first live Phase 2 acceptance batch against the current runtime data.

It exists to prove the real operator loop, not a fixture-only version:

1. create drafts from current `source_item_id` values,
2. inspect draft health before review,
3. optionally apply bounded micro-skills,
4. record review outcomes,
5. inspect draft health again,
6. capture what the current Content Engine still needs.

## Important Context

This batch uses the current runtime source items in `data/source_items.jsonl`.

That matters because the runtime state was intentionally reseeded during Phase 1 stabilization, so the older shortlist documents are still useful planning artifacts but not the exact live queue for this batch.

## Batch Composition

| source_item_id | source_id | raw_title | template_id | draft_id | pre_review_quality |
|---|---|---|---|---|---|
| `b3b1fae29b000493955232a2574e3317f0c8e375` | `src_curious_cuisiniere` | `Pak Mo Krob (Thai Vietnamese Crispy Rice Paper Wrap)` | `blog_food_fact_v1` | `draft-b3b1fae29b00-20260402T223452Z-f6c2b710` | `review_flag` |
| `5d1d078eb1ee712d2d76cd96a5578e47b9cf7543` | `src_saveur` | `Tsoureki (Greek Easter Bread)` | `blog_food_fact_v1` | `draft-5d1d078eb1ee-20260402T223503Z-1d67fdad` | `pass` |
| `0637ac87046ef3cc65bc45e52155c9f627622329` | `src_mashed` | `How To Give Your Costco Croissant Container A Second Life` | `blog_curiosity_food_v1` | `draft-0637ac87046e-20260402T223513Z-f74c7982` | `pass` |
| `c421b428894b627aa30123361debffe193871270` | `src_mashed` | `The Only 2 Foods Jacques Pépin Thinks Twice About Eating` | `blog_food_fact_v1` | `draft-c421b428894b-20260402T223521Z-9ab617b3` | `pass` |

## Commands Used

```powershell
python src\cli\create_draft_from_source_item.py --source-item-id b3b1fae29b000493955232a2574e3317f0c8e375
python src\cli\create_draft_from_source_item.py --source-item-id 5d1d078eb1ee712d2d76cd96a5578e47b9cf7543
python src\cli\create_draft_from_source_item.py --source-item-id 0637ac87046ef3cc65bc45e52155c9f627622329
python src\cli\create_draft_from_source_item.py --source-item-id c421b428894b627aa30123361debffe193871270
python src\cli\summarize_draft_health.py --json
python src\cli\apply_draft_micro_skills.py --draft-id draft-0637ac87046e-20260402T223513Z-f74c7982 --skill generate_headline_variants --skill generate_excerpt
python src\cli\review_draft.py --draft-id draft-b3b1fae29b00-20260402T223452Z-f6c2b710 --outcome rejected --note "reject_not_worth_slot: recipe-heavy wording and medium derivative risk make this draft too weak for the current queue."
python src\cli\review_draft.py --draft-id draft-5d1d078eb1ee-20260402T223503Z-1d67fdad --outcome needs_edits --note "intro_fix: replace low-signal terms like 'until' and 'bowl' with direct framing about braided Greek Easter bread and its symbolism."
python src\cli\review_draft.py --draft-id draft-0637ac87046e-20260402T223513Z-f74c7982 --outcome needs_edits --note "intro_fix: replace placeholder term list like 'container, plastic, and your' with clear reuse and food-storage framing before queueing." --note "headline_fix: do not use the current heuristic headline variants without manual cleanup."
python src\cli\review_draft.py --draft-id draft-c421b428894b-20260402T223521Z-9ab617b3 --outcome needs_edits --note "intro_fix: replace generic kitchen-result framing with a direct explanation that Jacques Pepin dislikes coconut and marshmallows."
python src\cli\summarize_draft_health.py --json
```

## Pre-Review Draft Health

Summary before review:

1. `4` total drafts
2. `3` drafts with `quality_gate_status = pass`
3. `1` draft with `quality_gate_status = review_flag`
4. `3` drafts with operator signal `ready_for_review`
5. `1` draft with operator signal `review_flag_pending`
6. `0` drafts with headline variants before enrichment
7. `4` drafts with excerpts

Interpretation:

1. the structural pipeline worked,
2. the quality layer did catch one derivative-risk issue,
3. the current deterministic quality gates still allow semantically awkward drafts to pass.

## Micro-Skill Observation

Bounded micro-skills were applied only to the Costco croissant container draft.

Observed result:

1. excerpt generation stayed inside scope,
2. headline variant generation remained bounded,
3. the heuristic headline variants were visibly awkward and not queue-ready.

This is a useful result, not a failure to hide. It confirms that the current heuristic provider is safe enough to test but not strong enough to trust without manual review.

## Review Outcomes

| draft_id | outcome | review reasoning |
|---|---|---|
| `draft-b3b1fae29b00-20260402T223452Z-f6c2b710` | `rejected` | The draft stayed too recipe-shaped and still carried medium derivative risk for a short explainer. |
| `draft-5d1d078eb1ee-20260402T223503Z-1d67fdad` | `needs_edits` | The draft passed the current gates, but low-signal terms like `until` and `bowl` made the intro and body framing too weak. |
| `draft-0637ac87046e-20260402T223513Z-f74c7982` | `needs_edits` | The draft passed structurally, but the phrasing still used placeholder-like term lists and the heuristic headline variants were not publishable. |
| `draft-c421b428894b-20260402T223521Z-9ab617b3` | `needs_edits` | The angle was understandable, but the opening framing stayed too generic and did not clearly explain the actual fact. |

## Post-Review Draft Health

Summary after review:

1. `4` total drafts
2. `3` drafts now in `approval_state = needs_edits`
3. `1` draft now in `approval_state = rejected`
4. `3` drafts now show operator signal `needs_revision`
5. `1` draft now shows operator signal `rejected`
6. `1` draft now contains headline variants from the bounded micro-skill pass

Interpretation:

1. the review loop works,
2. the health report reflects the current operator state correctly,
3. the batch is not yet strong enough for Phase 3 handoff.

## Most Important Findings

### 1. The mechanical Phase 2 loop is working

We can now do the full operator path:

1. source item -> draft
2. draft -> health summary
3. optional micro-skill pass
4. review decision
5. updated health summary

That is a real foundation milestone.

### 2. Structural quality is ahead of semantic quality

The current formatter can produce structurally complete drafts that still sound wrong at the wording level.

Examples seen in this batch:

1. `until, bowl, and greek easter`
2. `container, plastic, and your`
3. `coconut, jacques, and foods`

This means the current quality gates are necessary but not yet sufficient.

### 3. Topic-term extraction is the clearest current quality gap

The main deterministic weakness is not section count or storage. It is the content-selection logic that chooses which terms become the framing language for intros and sections.

### 4. Human review is doing exactly what it should do

The draft-health layer did not replace review. It made review easier to manage.

This batch confirms why v1 still needs:

1. human approval,
2. visible review notes,
3. draft-health summaries across the whole batch.

### 5. The current heuristic micro-skill provider is safe but weak

It did not break the draft shape.

But it also did not solve the core wording problem. That is important because it prevents us from pretending that a light heuristic layer has already fixed content quality.

## What This Means For Phase 2

Phase 2 is now stronger operationally, but not yet closeout-ready from a quality perspective.

The next high-value quality work should focus on:

1. improving topic-term extraction and filtering,
2. adding semantic coherence checks that catch low-signal phrasing before review,
3. improving or constraining heuristic headline generation so awkward variants are surfaced as scratch suggestions, not implied publish candidates.

## Conclusion

This batch was successful as a foundation step even though it produced no approvals.

That is the professional outcome:

1. the repo can now prove what works,
2. the repo can now show what still needs improvement,
3. future content-quality work can build on recorded evidence instead of vague intuition.
