# AI-Assisted Content Quality Policy V1

## Purpose

This document defines how external AI should be introduced later to improve content quality without changing the architecture of the project.

## Core Rule

External AI is a quality layer, not a foundation layer.

The system must still work without it.

## First Provider Principle

The likely first provider may be OpenAI, but the repo should stay provider-aware rather than provider-locked.

That means:

1. provider-backed skills should sit behind the existing micro-skill layer,
2. deterministic and heuristic fallback should remain available,
3. local provider credentials should remain optional and non-committed.

## Allowed Scope

Provider-backed AI may later improve:

1. headline variants,
2. short intros,
3. excerpts,
4. tightly bounded section smoothing,
5. later limited Facebook packaging text.

It must not own:

1. full article generation,
2. source selection,
3. template selection,
4. publish decisions,
5. winner decisions.

## Secret Handling Rule

If OpenAI or another provider is added later:

1. keep credentials in a local environment variable such as `OPENAI_API_KEY` or an ignored local config file,
2. do not commit provider secrets,
3. do not make provider setup a hard requirement for the base system.

## Review Rule

All provider-backed text remains reviewable proposed output, not trusted truth.

## Definition Of Done

This policy is satisfied when the later AI phase can improve text quality while preserving:

1. deterministic fallback,
2. clear review boundaries,
3. cost control,
4. transparent logging.
