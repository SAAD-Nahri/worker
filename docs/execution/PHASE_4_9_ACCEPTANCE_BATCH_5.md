# Phase 4.9 Acceptance Batch 5

## Scope

This acceptance batch records the detail-context hardening pass for the Approval UI baseline.

The goal of this batch is to prove that:

1. draft review detail now surfaces source lineage and headline suggestions more clearly,
2. social review detail now surfaces linked draft and linked blog context more clearly,
3. queue detail now surfaces mapping and selected-output context more clearly.

## What Changed

### WordPress admin plugin

The detail screens now expose more of the context that was already available in the operator API payloads.

Draft detail now shows:

1. source title,
2. source published time,
3. source URL link,
4. downstream blog/social ids,
5. headline suggestions.

Social detail now shows:

1. linked blog URL when present,
2. linked draft headline,
3. linked draft excerpt,
4. linked draft template/category context.

Queue detail now shows:

1. linked mapping status,
2. mapping id,
3. selected hook,
4. selected caption,
5. selected comment CTA.

## Validation Baseline

Python validation:

```powershell
python -m unittest discover -s tests -v
```

Accepted result:

1. full suite green at `225` tests passing.

## Known Limit

The plugin still requires live WordPress-admin validation because PHP CLI is not available in the local repo environment.

So this batch is accepted as:

1. plugin-context improved,
2. repo baseline preserved,
3. still awaiting live admin verification.
