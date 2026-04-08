# Phase 4.7 Acceptance Batch 1

## Scope

This batch closes the first operator-reviewed media baseline for blog and Facebook outputs.

The implemented slice adds:

1. append-only `media_brief_records.jsonl`, `asset_records.jsonl`, and `asset_review_records.jsonl`,
2. approved-draft media brief generation tied to draft, blog, and social lineage,
3. provenance-tagged asset registration for `owned`, `licensed`, and `ai_generated` assets,
4. explicit operator asset review with append-only approval history,
5. asset-readiness visibility in distribution health, operator API detail payloads, queue context, and validation reporting.

## Manual Interfaces

The first operator-facing media commands are:

1. `python src\cli\create_media_brief.py --draft-id <draft_id> [--blog-publish-id <id>] [--social-package-id <id>]`
2. `python src\cli\register_media_asset.py --media-brief-id <id> --asset-source-kind owned|licensed|ai_generated --provenance-reference <value> --asset-url-or-path <value> --alt-text <value>`
3. `python src\cli\review_media_asset.py --asset-record-id <id> --review-outcome approved|needs_edits|rejected --review-note <note>`

The first operator API media endpoints are:

1. `GET /media-assets/inbox`
2. `GET /media-assets/{asset_record_id}`
3. `POST /media-assets/{asset_record_id}/review`

## Validation Evidence

Focused validation:

```powershell
python -m unittest tests.unit.media_engine.test_media_flow tests.unit.distribution_engine.test_health tests.unit.operator_api.test_app -v
```

Full regression baseline:

```powershell
python -m unittest discover -s tests -v
```

Current green baseline: `253` passing tests.

## Acceptance Notes

What this batch proves:

1. one approved draft can now receive a bounded media brief,
2. one selected asset can be recorded with provenance and intended usage,
3. one asset review can be appended without mutating prior state,
4. linked blog and social outputs can see whether an approved asset is actually present,
5. the repo now has a rights-safe first visual baseline instead of treating media as an undefined side task.

What this batch does not yet claim:

1. no automatic asset generation or upload transport,
2. no in-plugin media review screen yet,
3. no WordPress featured-image upload adapter yet,
4. no broad visual library management or experimentation layer.
