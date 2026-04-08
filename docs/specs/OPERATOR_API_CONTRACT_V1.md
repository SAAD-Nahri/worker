# Operator API Contract V1

## Purpose

This spec defines the first internal operator API that powers the approval UI.

The API exists to expose review-safe operator actions over the existing append-only runtime records. It is not a second workflow engine, not a public publishing API, and not a replacement source of truth.

## Core Rule

The repo runtime remains authoritative.

The operator API must:

1. read current state from existing runtime records,
2. write review and scheduling actions by calling the same internal review/update paths the CLI uses,
3. preserve append-only behavior,
4. keep human approval explicit,
5. refuse shortcuts that bypass existing audit and approval boundaries.

## Architecture Position

The Operator API sits between:

1. the Python workflow engine and runtime records,
2. the WordPress admin approval plugin,
3. later optional internal tooling.

It is a thin internal service layer, not a public app surface.

## Security Model

The first security model is:

1. WordPress admin auth for who can access the plugin,
2. shared-secret auth for plugin-to-backend requests,
3. loopback or private-network hosting for the API when possible,
4. docs disabled by default unless intentionally enabled in local config.

The API currently expects:

1. `X-Content-Ops-Shared-Secret`

The shared secret must come from:

1. `config/operator_api.local.json`, or
2. environment variables supported by the operator API config loader.

## Default Config Contract

The default config file is:

1. `config/operator_api.local.json`

Safe example:

1. [operator_api_config.example.json](C:/Users/Administrator/OneDrive/Documents/co_ma/config/operator_api_config.example.json)

Required fields:

1. `bind_host`
2. `bind_port`
3. `shared_secret`
4. `enable_docs`

## Source Of Truth Rule

The API must not move workflow state into:

1. plugin-local storage,
2. WordPress post meta,
3. WordPress custom tables,
4. separate operator-UI database tables.

It may only expose or append to the repo runtime records already defined by the system.

## Endpoint Set

### `GET /dashboard/summary`

Purpose:

1. show the operator what needs attention now.

Response groups:

1. draft counts,
2. social package counts,
3. media-asset counts,
4. queue counts,
5. transport and activation failures,
6. recent review activity,
7. current alerts,
8. priority draft items,
9. priority social-package items,
10. priority media-asset items,
11. priority queue items,
12. fast-lane placeholder,
13. basic snapshot metadata.

Recent review activity rows should also expose safe detail-target hints so the UI can deep-link to the relevant review surface without guessing from raw ids alone.

Current alerts should expose a related `queue_item_id` whenever the backend can safely resolve the alert to one concrete queue review target.

### `GET /drafts/inbox`

Purpose:

1. list reviewable drafts from the latest draft and review state.

Each row should include:

1. `draft_id`
2. `source_item_id`
3. `source_domain`
4. `template_id`
5. `category`
6. `quality_gate_status`
7. `derivative_risk_level`
8. `routing_action`
9. `approval_state`
10. timestamps needed for ordering or review context.

Supported query filters:

1. `search`
2. `approval_state`
3. `operator_signal`
4. `source_domain`
5. `template_id`
6. `category`

### `GET /drafts/{draft_id}`

Purpose:

1. provide one review-complete draft detail payload.

Required context:

1. latest draft snapshot,
2. source lineage,
3. review history,
4. downstream linkage if present,
5. linked media brief and asset summaries when present,
6. read-only `ai_assistance_log` provenance when present,
7. fast-lane placeholder.

### `POST /drafts/{draft_id}/review`

Purpose:

1. record append-only draft review decisions.

Request fields:

1. `review_outcome`
2. `review_notes`
3. `reviewer_label`

Behavior:

1. use the same draft review logic as the CLI path,
2. append both the updated draft snapshot and draft review record,
3. return the refreshed draft detail payload.

### `POST /drafts/{draft_id}/select-headline-variant`

Purpose:

1. let the operator select one already-prepared headline variant without opening free-form editing.

Behavior:

1. only accept values that already exist in `headline_variants`,
2. append a refreshed draft snapshot,
3. re-run draft quality evaluation against the linked source item,
4. reopen the draft to `pending_review` / `drafted` because the selected headline changed.

### `GET /social-packages/inbox`

Purpose:

1. list reviewable Facebook package records.

Each row should include:

1. `social_package_id`
2. `blog_publish_id`
3. linked blog title
4. hook preview
5. caption preview
6. comment CTA preview
7. approval state
8. linkage state
9. review timestamps

Supported query filters:

1. `search`
2. `approval_state`
3. `linkage_state`

### `GET /social-packages/{social_package_id}`

Purpose:

1. provide one review-complete social package detail payload.

Required context:

1. latest package snapshot,
2. linked blog publish snapshot when present,
3. linked asset snapshot and readiness state when present,
4. linked draft summary plus draft `ai_assistance_log`,
5. social-package `ai_assistance_log`,
6. review history,
7. fast-lane placeholder.

### `POST /social-packages/{social_package_id}/review`

Purpose:

1. record append-only social package review decisions.

Behavior:

1. use the same review logic as the CLI path,
2. append updated social package and social review records,
3. refresh queue and mapping snapshots when blog linkage exists,
4. return the refreshed detail payload.

### `POST /social-packages/{social_package_id}/select-variant`

Purpose:

1. let the operator switch among already-prepared social variants before final approval.

Behavior:

1. only accept values that already exist in the package `variant_options`,
2. append a refreshed social-package snapshot,
3. refresh queue and mapping snapshots when blog linkage exists,
4. reopen approval to `pending_review` if the selected output changed after approval.

### `GET /media-assets/inbox`

Purpose:

1. list reviewable media assets tied to approved draft, blog, and social context.

Each row should include:

1. `asset_record_id`
2. `media_brief_id`
3. draft, blog, and social linkage ids
4. asset source kind
5. approval state
6. intended usage
7. provenance reference
8. linked blog title when present
9. asset completeness state
10. review timestamps

Supported query filters:

1. `search`
2. `approval_state`
3. `asset_source_kind`

### `GET /media-assets/{asset_record_id}`

Purpose:

1. provide one review-complete media-asset detail payload.

Required context:

1. latest asset snapshot,
2. linked media brief,
3. linked draft summary,
4. linked blog publish snapshot when present,
5. linked social package snapshot when present,
6. asset readiness state,
7. review history,
8. fast-lane placeholder.

### `POST /media-assets/{asset_record_id}/review`

Purpose:

1. record append-only media asset review decisions.

Behavior:

1. use the same review logic as the CLI path,
2. append updated asset and asset-review records,
3. preserve provenance and publish-chain linkage,
4. return the refreshed detail payload.

### `GET /queue/inbox`

Purpose:

1. list queue-visible publish chains that need review or scheduling attention.

Each row should include:

1. `queue_item_id`
2. `queue_type`
3. title
4. `queue_state`
5. `queue_review_state`
6. linked asset readiness context
7. schedule context
8. collision warnings
9. linked blog and social identifiers
10. `approve_allowed`
11. `approve_block_reason`
12. `schedule_allowed`
13. `schedule_block_reason`

Supported query filters:

1. `queue_type`
2. `queue_state`
3. `queue_review_state`
4. `blocked_only`
5. `schedule_allowed`

### `GET /queue/{queue_item_id}`

Purpose:

1. provide one review-complete queue detail payload.

Required context:

1. latest queue item snapshot,
2. linked blog publish snapshot,
3. linked social package snapshot when present,
4. linked asset snapshot and readiness state when present,
5. latest mapping snapshot when present,
6. schedule context,
7. review history,
8. action availability context,
9. fast-lane placeholder.

### `POST /queue/{queue_item_id}/approve`

Purpose:

1. append an explicit queue review decision.

Allowed outcomes in V1:

1. `approved`
2. `hold`
3. `removed`

Behavior:

1. append a queue review record,
2. do not mutate existing queue records in place,
3. return refreshed queue detail state.

### `POST /queue/{queue_item_id}/schedule`

Purpose:

1. let the operator set schedule intent from the approval UI.

Important V1 limit:

1. only `blog_publish` queue items can be directly scheduled through this endpoint.

Behavior:

1. require an approved queue review first,
2. append a scheduled blog publish snapshot,
3. refresh queue and mapping state,
4. return refreshed queue detail state.

Facebook scheduling remains a later transport-stage action and is intentionally not shortcut through the Approval UI V1 API.

## Action Availability Rule

Queue-facing payloads should tell the UI whether direct schedule action is available instead of forcing the UI to discover that only by failed submission.

For Approval UI V1:

1. failed queue items should return `approve_allowed = false` with a human-readable `approve_block_reason`,
2. only blog queue items can ever return `schedule_allowed = true`,
3. queue scheduling requires an approved queue review first,
4. queue scheduling must still satisfy the existing blog-scheduling rules from the distribution layer,
5. when scheduling is not allowed, the payload should return a human-readable `schedule_block_reason`,
6. queue detail payloads should also expose `remove` as an allowed review action in V1.

### `GET /health/combined`

Purpose:

1. expose a compact combined operator-health view for the approval shell.

It should include:

1. draft health summary,
2. distribution health summary,
3. distribution schedule summary,
4. activation readiness summary,
5. fast-lane placeholder.

### `GET /validation/operator-baseline`

Purpose:

1. give the WordPress admin plugin one dedicated backend-readiness surface for live admin validation.

It should include:

1. endpoint check results for the approval shell,
2. workflow snapshot counts,
3. record visibility counts,
4. review-surface availability flags, including media review,
5. validation notes,
6. combined health context.

## Response Shape Principle

Responses should be grouped around operator tasks, not raw storage tables.

Payload categories are:

1. dashboard summary,
2. inbox rows,
3. detail view payloads,
4. action responses,
5. combined health snapshot.

## AI Provenance Rule

The operator API may expose AI usage metadata as read-only provenance, but it must not expose provider-generation actions in this phase.

Visible provenance is limited to:

1. `skill_name`,
2. `target_field`,
3. `model_label`,
4. `created_at`.

## Fast-Lane Rule

The operator API should already expose a placeholder for later score-assisted review, but it must remain disabled.

The placeholder should make clear:

1. status is disabled,
2. autoapproval is not active,
3. the capability belongs to Phase 5.5,
4. no current decision is skipped because of score.

## V1 Validation Baseline

The Python-side baseline should prove:

1. auth failures are rejected correctly,
2. inbox endpoints reflect runtime state correctly,
3. detail endpoints include review context,
4. review endpoints append the expected records,
5. media review endpoints preserve provenance and linkage,
6. queue schedule rules enforce the current architecture boundary,
7. the combined health endpoint remains available for the operator shell,
8. the validation endpoint remains available for the live WordPress-admin validation page.

## V1 Limits

This API does not yet:

1. expose public publishing shortcuts,
2. expose in-plugin media generation or asset-upload automation,
3. expose analytics dashboards,
4. expose autoapproval controls,
5. replace live transport workflows.
