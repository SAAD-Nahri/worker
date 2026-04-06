# Facebook Graph Transport V1

## Purpose

This document defines the first real Facebook transport adapter for Phase 3.

The adapter is intentionally narrow:

1. it publishes or schedules the main Facebook Page feed post for an approved `SocialPackageRecord`
2. it is dry-run by default
3. it records success or failure through the existing append-only Facebook publish workflow
4. it does not bypass queue or mapping refresh

## Selected First Transport

The first supported Facebook transport is:

1. Facebook Graph API
2. Page feed posting
3. Page access token authentication
4. main post transport only

This choice is good for v1 because it is:

1. aligned with the project's Facebook Page-first distribution model
2. simpler than media-heavy or multi-step variants
3. compatible with the current `SocialPackageRecord` and `FacebookPublishRecord` model
4. easy to preview safely before execution

## Scope

The v1 transport layer covers:

1. loading a local operator config file
2. building a deterministic Graph API request from an approved `SocialPackageRecord`
3. previewing the request without mutating runtime state
4. executing a Page feed post create request against Facebook
5. recording `scheduled`, `published`, or `failed` Facebook publish snapshots
6. refreshing queue and mapping snapshots after execution

It does not yet cover:

1. auto-posting the comment CTA line
2. Facebook Groups
3. media uploads
4. retries or backoff
5. edit/update flows for an existing Facebook post

## Required Config Fields

The transport config must contain:

1. `page_id`
2. `page_access_token`

Optional fields:

1. `api_version`
2. `timeout_seconds`

### Config Rules

1. `page_access_token` is sensitive and must not be committed into the repo.
2. if the operator keeps a config file inside the repo, the recommended ignored filename is `facebook_graph_config.local.json`.
3. `api_version` should be explicit so transport behavior is traceable over time.

## Input Contract

The transport starts from:

1. an approved `SocialPackageRecord`
2. the linked `BlogPublishRecord`
3. an explicit remote action: `published` or `scheduled`

Minimum acceptable input:

1. `social_package_id`
2. `blog_publish_id`
3. `hook_text`
4. `caption_text`
5. confirmed `blog_url`
6. `approval_state = approved`

## Main Message Rule

The first transport publishes the main Page post only.

The main request message should be composed from:

1. `hook_text`
2. a blank line
3. `caption_text`

The `blog_url` should be sent through the Graph API `link` field.

The `comment_cta_text` remains part of the selected package record, but it is intentionally deferred from live transport in this first slice.

## Blog-State Safety Rules

The transport must not outrun the blog.

Rules:

1. `published` Facebook transport requires the linked blog publish record to already be `published`
2. `scheduled` Facebook transport requires the linked blog publish record to already be `scheduled` or `published`
3. `scheduled` Facebook transport must not be earlier than the linked blog schedule

This keeps the first live transport slice aligned with the repo's existing scheduling policy instead of creating a new exception path.

## Request Rules

The first request endpoint is:

1. `POST https://graph.facebook.com/{api_version}/{page_id}/feed`

The request payload must include:

1. `message`
2. `link`

For `scheduled` actions the request must also include:

1. `published=false`
2. `scheduled_publish_time`

## Dry-Run Behavior

Dry-run is the default operator mode.

Dry-run must:

1. build the exact request that would be executed
2. return the target URL, method, form fields, selected action, and deferred comment CTA text
3. enforce the same publish-safety rules as execute mode
4. avoid writing any new Facebook publish, queue, or mapping records
5. avoid any network request

## Execute Behavior

When `--execute` is used, the adapter must:

1. send the Graph API request to Facebook
2. require a remote Facebook post id in the response
3. map a successful `published` action to a local `published` Facebook publish snapshot
4. map a successful `scheduled` action to a local `scheduled` Facebook publish snapshot
5. append the updated Facebook publish snapshot
6. refresh queue and mapping records immediately after the append

## Failure Behavior

When the remote request fails, the adapter must:

1. preserve the original selected package
2. append a new `failed` Facebook publish snapshot with the visible error
3. refresh queue and mapping records from that failed snapshot
4. return a non-zero CLI exit code

This keeps operator trust intact because remote errors remain visible in the same append-only workflow as manual Facebook publish-state changes.

## Security Rules

1. do not print the page access token
2. do not embed access secrets in repo docs or committed config files
3. do not mutate approved social packages during transport
4. do not auto-post comment CTA text silently in this first slice

## CLI Contract

The operator entry point is:

`python src\cli\sync_facebook_transport.py --social-package-id <social_package_id> --action published --config-path <path>`

For scheduled transport:

`python src\cli\sync_facebook_transport.py --social-package-id <social_package_id> --action scheduled --scheduled-for-facebook <timestamp> --schedule-mode manual --config-path <path>`

Execution must be explicit:

1. add `--execute` to send the remote request

## Definition Of Done

This spec is satisfied when:

1. an approved social package can be previewed as a real Facebook Graph Page feed request
2. the same package can be executed safely against a Facebook Page
3. success and failure both flow back into append-only Facebook publish, queue, and mapping records
4. dry-run remains the default operator mode
