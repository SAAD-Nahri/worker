# Facebook Transport Validation V1

## Purpose

This document defines the first non-mutating validation workflow for the Facebook Graph transport.

The goal is to let the operator confirm:

1. the Facebook config file loads correctly,
2. the configured Page is reachable,
3. the Page access token is valid,
4. the repo can identify the target Page before post transport execution begins.

## Core Rule

Validation must not create a post.

The validation step exists to confirm environment readiness before live publish or schedule requests are attempted.

## Scope

The v1 validation layer covers:

1. loading the operator Facebook config,
2. building a deterministic validation request,
3. previewing the request in dry-run mode,
4. executing a read-only Graph request,
5. surfacing the validated Page id and Page name.

It does not yet cover:

1. comment-post permission validation,
2. media upload validation,
3. Facebook Groups,
4. app-review readiness beyond owned test Pages,
5. post-creation permission nuance across multiple Page roles.

## Selected Endpoint

The first validation endpoint is:

`GET https://graph.facebook.com/{api_version}/{page_id}?fields=id,name`

This endpoint is good for v1 because it:

1. proves the Page id and Page access token work together,
2. confirms that the repo is pointed at the expected Page,
3. avoids mutating the Page feed.

## Dry-Run Rule

Dry-run is the default mode.

Dry-run must:

1. return the exact request URL and method,
2. avoid making any network request,
3. avoid mutating runtime state,
4. avoid printing the access token.

## Execute Rule

When `--execute` is used, validation must:

1. send the read-only request,
2. require a remote Page id in the response,
3. surface the Page name when available,
4. return a non-zero exit code on failure.

## Security Rules

1. do not print the Page access token,
2. do not commit the operator config file,
3. do not treat validation success as permission to bypass dry-run in the real Page-post transport.

## CLI Contract

Preview:

`python src\cli\validate_facebook_transport.py --config-path <facebook_graph_config.json>`

Execute:

`python src\cli\validate_facebook_transport.py --config-path <facebook_graph_config.json> --execute`

## Definition Of Done

This spec is satisfied when:

1. the repo can preview a Facebook validation request safely,
2. the repo can execute a read-only Page identity check safely,
3. the operator can confirm the target Page identity before live Facebook transport begins.
