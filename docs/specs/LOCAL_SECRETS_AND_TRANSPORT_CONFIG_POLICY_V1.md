# Local Secrets And Transport Config Policy V1

## Purpose

This document defines how the operator stores and uses local transport credentials for the current WordPress and Facebook integrations.

The goal is to make live activation possible without letting secret handling drift into guesswork.

## Core Rule

Secrets must remain local and non-committed.

The repo may contain:

1. safe example files,
2. safe local-path recommendations,
3. docs that describe required fields.

The repo must not contain:

1. real application passwords,
2. real Facebook Page access tokens,
3. copied production config values,
4. screenshots or logs that expose secrets.

## Approved Local Config Locations

The current recommended repo-local ignored filenames are:

1. `config/wordpress_rest_config.local.json`
2. `config/facebook_graph_config.local.json`

The root-level ignored alternatives remain acceptable:

1. `wordpress_rest_config.local.json`
2. `facebook_graph_config.local.json`

The `config/` location is preferred because it keeps operator setup visible without mixing secrets into top-level project files.

## WordPress Config Contract

The current WordPress local config file must contain:

1. `base_url`
2. `username`
3. `application_password`

It should also contain:

1. `category_id_by_name`
2. `tag_id_by_name`
3. `timeout_seconds`

Notes:

1. `base_url` must begin with `http://` or `https://`,
2. `category_id_by_name` is operationally important because WordPress draft sync expects a resolvable category id,
3. `tag_id_by_name` may be partial at first, but missing tags should be an intentional choice.

## Facebook Config Contract

The current Facebook local config file must contain:

1. `page_id`
2. `page_access_token`

It may also contain:

1. `api_version`
2. `timeout_seconds`

Notes:

1. the token must belong to an operator-owned Page or test Page,
2. v1 does not assume Group publishing,
3. v1 validation is Page-identity focused before live posting begins.

## Example Files

The safe example files are:

1. [config/wordpress_rest_config.example.json](C:/Users/Administrator/OneDrive/Documents/co_ma/config/wordpress_rest_config.example.json)
2. [config/facebook_graph_config.example.json](C:/Users/Administrator/OneDrive/Documents/co_ma/config/facebook_graph_config.example.json)
3. [config/README.md](C:/Users/Administrator/OneDrive/Documents/co_ma/config/README.md)

The operator should copy them into `.local.json` files and replace placeholder values locally.

## Logging Rules

1. do not print `application_password`,
2. do not print `page_access_token`,
3. do not paste live secrets into markdown docs,
4. do not store secrets inside runtime JSONL records,
5. treat config-path references as acceptable, but not config values.

## Operational Rules

1. dry-run validation remains the default first step,
2. execute-mode validation is allowed because it is read-only,
3. execute-mode transport should only be used after dry-run preview is understood,
4. one owned-environment canary chain should be used before broader live usage.

## Intentional Non-Goals

This policy does not yet require:

1. secret managers,
2. cloud vault integration,
3. CI secret injection,
4. multi-environment deployment profiles.

Those may be considered later, but they are not required for the current single-operator baseline.
