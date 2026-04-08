# Runtime Data

This directory now contains both committed configuration and generated runtime artifacts.

## Files

1. [source_registry.json](C:/Users/Administrator/OneDrive/Documents/co_ma/data/source_registry.json)
   The application-facing source registry. This is configuration and should remain part of the repo.

2. `source_items.jsonl`
   Append-only normalized source item records written by Source Engine runs.

3. `intake_history.jsonl`
   Append-only per-run summary records written by Source Engine runs.

4. `dedupe_index.json`
   The persistent dedupe memory used to identify repeat source items across runs.

5. `source_decisions.jsonl`
   Append-only source-review decision records written by the source review workflow.

6. `draft_records.jsonl`
   Append-only Content Engine draft records written by Phase 2 draft creation workflows.

7. `draft_reviews.jsonl`
   Append-only draft review records written by the Phase 2 review workflow.

8. `blog_publish_records.jsonl`
   Append-only Phase 3 blog publish preparation and publish-state records.

9. `social_package_records.jsonl`
   Append-only Phase 3 Facebook package preparation records.

10. `social_package_reviews.jsonl`
   Append-only Phase 3 social package review records.

11. `facebook_publish_records.jsonl`
   Append-only Phase 3 Facebook publish-state records.

12. `queue_item_records.jsonl`
   Append-only Phase 3 queue records for blog and Facebook workflow state.

13. `blog_facebook_mapping_records.jsonl`
   Append-only Phase 3 mapping records linking blog publish state to selected Facebook packaging.

14. `queue_review_records.jsonl`
   Append-only operator queue-review records used by the approval console and queue scheduling gate.

15. `tracking_audit_records.jsonl`
   Append-only Phase 4 audit records for deliberate normalization runs and execute-mode transport validation.

16. `media_brief_records.jsonl`
   Append-only Phase 4.7 media brief records derived from approved draft context.

17. `asset_records.jsonl`
   Append-only Phase 4.7 asset records preserving provenance, review state, and publish-chain linkage.

18. `asset_review_records.jsonl`
   Append-only Phase 4.7 asset review records for explicit operator media approval decisions.

19. `archive/<timestamp>/...`
   Archived runtime snapshots created by the explicit reset workflow.

20. `reports/<timestamp>/...`
   Optional scheduled JSON health and history snapshots created by the runtime reporting service examples.

## Operational Rules

1. `source_registry.json` is part of the planned system state and should be treated as intentional project input.
2. The other files are runtime state, not planning docs.
3. Re-running intake against the same feeds will naturally drive `exact_duplicate` counts up over time. That is expected, not a failure.
4. The append-only logs are useful for audit and iteration, but they are not the same thing as the long-term analytical layer.
5. When `--fetch-article-bodies` is used, the resulting source items will include richer `raw_body_text` plus body-extraction status metadata.
6. Source review decisions should be preserved even when a registry update is not applied.
7. A clean local run should archive runtime files first instead of deleting them casually.
8. Draft records are runtime state, not planning docs, even when they are produced from structured templates.
9. Draft review records are runtime state too, and should preserve the human approval trail for Phase 2.
10. Operator-facing draft health reporting should read these runtime files, not replace them.
11. Local WordPress-ready publish records are runtime state too, even before a remote WordPress transport is chosen.
12. Local Facebook-ready social package records are runtime state too, even before queue and transport layers are chosen.
13. Social package review records are runtime state too, and should preserve the manual approval trail for Facebook packaging.
14. Facebook publish records are runtime state too, and should preserve explicit scheduled, published, and failed Facebook-side outcomes before live transport is finalized.
15. Queue records are runtime state too, and should preserve operator-facing workflow state separately from content quality.
16. Mapping records are runtime state too, and should preserve the selected blog and Facebook values even before full publish tracking exists.
17. Queue review records are runtime state too, and should preserve append-only operator approval decisions separately from queue-item snapshots.
18. Draft health summaries are derived from `draft_records.jsonl` and `draft_reviews.jsonl`; they are not stored as their own runtime artifact in v1.
19. Distribution health summaries are derived from the Phase 3 publish, review, queue, and mapping records; they are not stored as their own runtime artifact in v1.
20. Phase 4 publish-chain history, exception, activity, and variant summaries are also derived on demand from the append-only runtime records; they are not stored as their own runtime artifact in v1.
21. Phase 4 tracking audit records are runtime state and should remain opt-in and low-volume; they are not a general event stream.
22. Optional `data/reports/` snapshots are derived operational outputs, not the source of truth for workflow state.
23. Media brief, asset, and asset-review records are runtime state too, and should preserve rights-safe provenance plus explicit visual approval for blog and Facebook outputs.

## Clean Local Re-run Guidance

If a clean local run is needed for development, keep `source_registry.json` and clear or archive only:

1. `source_items.jsonl`
2. `intake_history.jsonl`
3. `dedupe_index.json`
4. `source_decisions.jsonl`
5. `draft_records.jsonl`
6. `draft_reviews.jsonl`
7. `blog_publish_records.jsonl`
8. `social_package_records.jsonl`
9. `social_package_reviews.jsonl`
10. `facebook_publish_records.jsonl`
11. `queue_item_records.jsonl`
12. `queue_review_records.jsonl`
13. `blog_facebook_mapping_records.jsonl`
14. `tracking_audit_records.jsonl`
15. `media_brief_records.jsonl`
16. `asset_records.jsonl`
17. `asset_review_records.jsonl`

That choice should be explicit, because deleting the dedupe index changes run behavior.
