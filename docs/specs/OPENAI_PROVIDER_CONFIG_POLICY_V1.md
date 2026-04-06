# OpenAI Provider Config Policy V1

## Purpose

This document defines how OpenAI should be configured as the first optional provider-backed quality layer.

## Core Rule

OpenAI is optional.

The system must remain usable with no OpenAI configuration at all.

## Preferred Secret Path

The preferred local secret path is:

1. `OPENAI_API_KEY`

This keeps the provider credential out of repo-tracked files and aligns with the current single-operator baseline.

## Acceptable Fallback Path

If the operator prefers a file-based local setup, an ignored local config file is acceptable:

1. `config/openai_provider_config.local.json`

The repo may include a safe example file, but it must not include a real API key.

## Required Config Fields

The first provider config should support at minimum:

1. `api_key`
2. `model`
3. `timeout_seconds`

The local config file is a fallback convenience, not the preferred path.

## Logging Rules

1. do not print the API key,
2. do not write the API key into draft records, runtime logs, or acceptance docs,
3. only record provider-safe fields such as provider label or model label.

## Failure Rule

If OpenAI config is missing or invalid:

1. the micro-skill path must fall back to the heuristic provider by default,
2. the system must not stop being usable,
3. provider-selection errors should be explicit and non-secret-bearing.

## Definition Of Done

This policy is satisfied when OpenAI can be configured locally without:

1. becoming required,
2. exposing secrets,
3. weakening the heuristic fallback baseline.
