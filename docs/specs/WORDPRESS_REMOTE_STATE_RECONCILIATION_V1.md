# WordPress Remote State Reconciliation V1

## Purpose

Define the safe operator path for reading the real remote WordPress post state back into the system and, when appropriate, reconciling the local append-only blog publish chain from that result.

This spec exists because live activation can include a manual WordPress admin step between:

1. local draft preparation and remote draft sync,
2. remote publish or schedule in WordPress,
3. local queue and mapping refresh before Facebook transport.

Without an explicit reconciliation step, the repo can lag behind the real site state.

## Scope

This spec applies only to:

1. existing `blog_publish_id` chains that already have a remote `wordpress_post_id`,
2. read-only inspection of the remote WordPress post,
3. optional append-only local reconciliation from the inspected remote state.

It does not add:

1. new remote publish actions,
2. automatic Facebook transport,
3. automatic content edits,
4. background polling.

## Core Rule

Remote-state inspection must be safe by default.

That means:

1. inspection is read-only,
2. reconciliation is opt-in,
3. local updates remain append-only,
4. queue and mapping refreshes happen only after a deliberate reconciliation step.

## Operator Entry Point

The operator entry point is:

```powershell
python src\cli\reconcile_wordpress_post_state.py
```

The command must support:

1. dry-run preview without remote execution,
2. execute-mode remote inspection,
3. optional local reconciliation.

## Inputs

Required:

1. `blog_publish_id`
2. WordPress REST config path

Optional:

1. explicit `wordpress_post_id` override
2. schedule metadata for remote `future` reconciliation

Default behavior:

1. derive `wordpress_post_id` from the latest local blog publish record,
2. inspect only,
3. do not mutate local records unless the operator explicitly requests reconciliation.

## Remote Inspection Contract

Execute-mode inspection must request the real WordPress post state from:

```text
/wp-json/wp/v2/posts/<post_id>?context=edit
```

The inspected payload should preserve at minimum:

1. remote post id,
2. remote status,
3. remote URL,
4. remote slug,
5. remote title,
6. remote published/scheduled timestamp when available,
7. remote modified timestamp when available,
8. HTTP response status.

## Supported Remote Status Mapping

Remote WordPress statuses map to local actions like this:

1. `draft` -> `draft_updated` if a local remote post id already exists, otherwise `draft_created`
2. `auto-draft` -> same handling as `draft`
3. `future` -> `scheduled`
4. `publish` -> `published`

Unsupported remote statuses must not be silently coerced.

If the operator requests reconciliation for an unsupported status, the command must fail with an explicit error.

## Local Reconciliation Rules

When reconciliation is requested:

1. append a new local `BlogPublishRecord`
2. preserve append-only history
3. refresh queue records
4. refresh mapping records
5. preserve the confirmed remote `wordpress_post_url`

For `future`:

1. local reconciliation must require schedule metadata
2. default scheduling mode is `manual`
3. the remote scheduled timestamp becomes `scheduled_for_blog`

For `publish`:

1. the remote publish timestamp becomes `published_at_blog`
2. the local blog queue should resolve to `published_blog`

## Safety Limits

This reconciliation step must not:

1. publish or update remote WordPress content
2. trigger Facebook transport automatically
3. overwrite local history in place
4. assume that a successful remote inspection means the Facebook token is still valid

## Phase 4.5 Role

This is a Phase 4.5 activation support tool.

Its job is to close the gap between:

1. remote WordPress admin actions,
2. local append-only publish state,
3. queue and mapping truth before Facebook transport.

It is not a general synchronization subsystem and should stay that way unless a later phase explicitly expands the design.
