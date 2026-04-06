# Phase 2 Acceptance Batch 9

## Purpose

This batch records the final Phase 2 hardening pass completed after the formal closeout review.

The goal was to remove two quiet trust gaps before Phase 3 depends on approved drafts:

1. content-affecting micro-skill edits should not leave a draft in a stale approved state,
2. explicit template overrides should not be able to bypass the source item's template family.

## Why This Batch Was Needed

The post-closeout review surfaced two realistic failure modes:

1. `generate_short_intro` could rewrite draft content after approval without forcing a fresh quality pass or review cycle,
2. `--template-id` could force a source item through the wrong blog template family and still produce a structurally valid draft.

Neither gap broke the normal deterministic path, but both weakened downstream trust.

## Hardening Changes

### 1. Content-affecting micro-skills now reopen review

When `generate_short_intro` changes the intro text:

1. quality is re-evaluated immediately,
2. quality flags and derivative-risk fields are refreshed,
3. `approval_state` is reset to `pending_review`,
4. `workflow_state` is reset to `drafted`.

This means an approved draft cannot silently remain approved after a content change.

### 2. Intro generation now respects template guidance

`generate_short_intro` now uses the selected template's intro slot bounds instead of a single global intro range.

For the current intro-bearing templates, that keeps the rewritten intro inside the accepted `35` to `70` word guidance unless the provider output is still weak for some other reason.

### 3. Intro generation is blocked for templates without an intro slot

The curiosity template does not carry an intro slot in the accepted v1 contract.

The micro-skill path now rejects `generate_short_intro` for that template instead of quietly creating a contract mismatch.

### 4. Template overrides are now family-safe

Explicit template overrides remain allowed for operator control, but only when they stay inside the same template family as the source item's `template_suggestion`.

This prevents a curiosity-style source from being forced through a food-fact template just because the sections happen to validate structurally.

## Validation

Commands run for this batch:

```powershell
python -m unittest discover -s tests -v
python src\cli\replay_phase2_gold_set.py
```

Results:

1. `python -m unittest discover -s tests -v` -> `96` tests passing
2. `python src\cli\replay_phase2_gold_set.py` -> `14/14` passing

## Outcome

This batch strengthens the accepted Phase 2 contract in a practical way:

1. approved drafts are safer as Phase 3 upstream inputs,
2. micro-skill use is more template-aware,
3. operator overrides are narrower and more honest,
4. the post-closeout Phase 2 baseline is now easier to trust as a long-term foundation.
