# AI-Assisted Content Quality Policy V1

## Purpose

This document defines how external AI may improve content quality without changing the architecture of the project.

## Core Rule

External AI is a quality layer, not a foundation layer.

The system must still work without it.

## First Provider Principle

The first provider is OpenAI, but the repo should stay provider-aware rather than provider-locked.

That means:

1. provider-backed skills should sit behind the existing micro-skill layer,
2. deterministic and heuristic fallback should remain available,
3. local provider credentials should remain optional and non-committed,
4. provider setup should remain manual opt-in only.

## Allowed Scope

Provider-backed AI may improve:

1. headline variants,
2. short intros,
3. excerpts,
4. tightly bounded section smoothing later,
5. manual Facebook package refinement as full variant bundles.

It must not own:

1. full article generation,
2. source selection,
3. template selection,
4. publish decisions,
5. winner decisions,
6. transport execution.

## Secret Handling Rule

For OpenAI:

1. keep credentials in a local environment variable such as `OPENAI_API_KEY` or an ignored local config file,
2. do not commit provider secrets,
3. prefer `OPENAI_API_KEY` over file-based `api_key`,
4. do not make provider setup a hard requirement for the base system.

## Invocation Rule

Provider-backed quality must remain manual opt-in.

That means:

1. no automatic provider calls during draft creation,
2. no automatic provider calls during deterministic Facebook packaging,
3. no automatic provider calls during scheduling or transport,
4. no approval-UI generation buttons in this phase.

## Review Rule

All provider-backed text remains reviewable proposed output, not trusted truth.

Draft output may update accepted bounded fields, but content-affecting changes must still reopen review.

Social refinement must only append review-safe variants. It must not switch the active selected package automatically.

## Provenance Rule

Provider-backed changes must record review-visible provenance.

The minimum visible metadata is:

1. `skill_name`,
2. `target_field`,
3. `model_label`,
4. `created_at`.

## Definition Of Done

This policy is satisfied when the AI phase can improve text quality while preserving:

1. deterministic fallback,
2. clear review boundaries,
3. cost control,
4. transparent logging,
5. manual operator control over whether provider variants are actually selected.
