# WordPress Transport Validation V1

## Purpose

This document defines the first non-mutating validation workflow for the WordPress REST transport.

The goal is to let the operator confirm:

1. the config file loads correctly,
2. the endpoint is reachable,
3. the credentials are valid,
4. the repo can identify the authenticated WordPress user before draft sync execution begins.

## Core Rule

Validation must not mutate remote content.

The validation step exists to reduce operator guesswork before live draft sync, not to create or update a WordPress post.

## Scope

The v1 validation layer covers:

1. loading the operator WordPress config,
2. building a deterministic validation request,
3. previewing that request in dry-run mode,
4. executing a read-only authenticated validation request,
5. surfacing the validated user identity in a machine-readable result.

It does not yet cover:

1. validating category ids against the live site,
2. validating tag ids against the live site,
3. checking theme behavior,
4. creating test posts,
5. verifying scheduling or public publish permissions.

## Selected Endpoint

The first validation endpoint is:

`GET {base_url}/wp-json/wp/v2/users/me?context=edit`

This endpoint is good for v1 because it:

1. requires authenticated access,
2. proves that the base URL and credentials work together,
3. returns a concrete user identity without mutating content.

## Dry-Run Rule

Dry-run is the default mode.

Dry-run must:

1. return the exact request URL and method,
2. avoid making any network request,
3. avoid mutating runtime state,
4. avoid printing secrets.

## Execute Rule

When `--execute` is used, validation must:

1. send the read-only request,
2. require a remote user id in the response,
3. surface the validated user slug and display name when available,
4. return a non-zero exit code on failure.

## Security Rules

1. do not print the application password,
2. do not commit the operator config file,
3. do not treat validation success as permission to bypass dry-run in the real draft-sync transport.

## CLI Contract

Preview:

`python src\cli\validate_wordpress_transport.py --config-path <wordpress_rest_config.json>`

Execute:

`python src\cli\validate_wordpress_transport.py --config-path <wordpress_rest_config.json> --execute`

## Definition Of Done

This spec is satisfied when:

1. the repo can preview a WordPress validation request safely,
2. the repo can execute a read-only validation request safely,
3. the operator can confirm the authenticated WordPress identity before draft sync begins.
