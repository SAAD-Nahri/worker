# WordPress REST Transport V1

## Purpose

This document defines the first real WordPress transport adapter for Phase 3.

The adapter is intentionally narrow:

1. it syncs approved local blog publish records to remote WordPress drafts,
2. it is dry-run by default,
3. it records success or failure through the existing append-only publish workflow,
4. it does not bypass queue or mapping refresh.

## Selected First Transport

The first supported WordPress transport is:

1. WordPress REST API
2. application-password authentication
3. draft create and draft update only

This choice is good for v1 because it is:

1. simple,
2. widely supported,
3. compatible with the existing publish-record model,
4. easy to preview safely before execution.

## Scope

The v1 transport layer covers:

1. loading a local operator config file,
2. building a deterministic REST request from a `BlogPublishRecord`,
3. previewing the request without mutating runtime state,
4. executing the request against WordPress,
5. recording `draft_created`, `draft_updated`, or `failed` publish snapshots,
6. refreshing queue and mapping snapshots after execution.

It does not yet cover:

1. media upload,
2. featured images,
3. SEO plugin metadata,
4. retries or backoff,
5. schedule or publish-now transport actions,
6. Facebook transport.

## Required Config Fields

The transport config must contain:

1. `base_url`
2. `username`
3. `application_password`
4. `category_id_by_name`

Optional fields:

1. `tag_id_by_name`
2. `timeout_seconds`

### Config Rules

1. `base_url` must point at the WordPress site root.
2. `application_password` is sensitive and must not be committed into the repo.
3. category mappings are required and must be explicit.
4. tag mappings are optional; unmapped tags are skipped, not invented remotely.

### Example Config Shape

```json
{
  "base_url": "https://example.com",
  "username": "editor",
  "application_password": "xxxx xxxx xxxx xxxx xxxx xxxx",
  "category_id_by_name": {
    "Food Facts": 12
  },
  "tag_id_by_name": {
    "Kitchen Science": 44,
    "Ingredient Basics": 57
  },
  "timeout_seconds": 20
}
```
5. if the operator keeps a config file inside the repo, the recommended ignored filename is `wordpress_rest_config.local.json`.

## Input Contract

The transport starts from an existing local `BlogPublishRecord`, not directly from a draft.

Minimum acceptable input:

1. `blog_publish_id`
2. `wordpress_title`
3. `wordpress_slug`
4. `wordpress_excerpt`
5. `wordpress_body_html`
6. `wordpress_category`
7. `wordpress_status` not already `scheduled` or `published`

Operation selection:

1. if `wordpress_post_id` is empty, use `create_draft`
2. if `wordpress_post_id` already exists, use `update_draft`

## Request Build Rules

The request payload must include:

1. `title`
2. `slug`
3. `excerpt`
4. `content`
5. `status = draft`
6. `categories`
7. `tags` only when one or more mapped tag IDs exist

Category mapping rule:

1. missing category mapping is a hard error

Tag mapping rule:

1. missing tag mappings are recorded as skipped tag names in the dry-run preview
2. skipped tags do not block draft sync

## Dry-Run Behavior

Dry-run is the default operator mode.

Dry-run must:

1. build the exact request that would be executed,
2. return the target URL, method, payload, resolved category ID, resolved tag IDs, and skipped tag names,
3. avoid writing any new publish, queue, or mapping records.

This is a safety requirement, not a convenience feature.

## Execute Behavior

When `--execute` is used, the adapter must:

1. send the REST request to WordPress,
2. require a remote post ID in the response,
3. accept a missing remote `status` when the response is otherwise valid,
4. reject returned remote statuses that are clearly outside draft sync, such as `published`,
5. map a successful create to local `draft_created`,
6. map a successful update to local `draft_updated`,
7. append the updated blog publish snapshot,
8. refresh queue and mapping records immediately after the append.

## Failure Behavior

When the remote request fails, the adapter must:

1. preserve the original local payload,
2. append a new `failed` blog publish snapshot with the visible error,
3. refresh queue and mapping records from that failed snapshot,
4. return a non-zero CLI exit code.

This keeps operator trust intact because remote errors remain visible in the same append-only workflow as manual publish-state changes.

## Security Rules

1. do not print the application password,
2. do not embed auth secrets in repo docs or committed config files,
3. do not mutate approved drafts during transport,
4. do not let transport logic invent taxonomy values that were never approved upstream.

## CLI Contract

The operator entry point is:

`python src\cli\sync_wordpress_transport.py --blog-publish-id <blog_publish_id> --config-path <path>`

Execution must be explicit:

`python src\cli\sync_wordpress_transport.py --blog-publish-id <blog_publish_id> --config-path <path> --execute`

## Definition Of Done

This spec is satisfied when:

1. a prepared local blog publish record can be previewed as a WordPress REST draft request,
2. the same record can be executed safely against WordPress with application-password auth,
3. success and failure both flow back into append-only publish, queue, and mapping records,
4. dry-run remains the default operator mode.
