# Phase 4.6 Validation Plan

## Purpose

This document defines how the AI-assisted content-quality phase should be validated.

The focus is bounded quality improvement with controlled failure behavior.

## Validation Layers

Phase 4.6 validation has five layers:

1. repo baseline validation,
2. provider-config validation,
3. provider-adapter validation,
4. regression validation for no-provider fallback,
5. bounded acceptance replay.

## 1. Repo Baseline Validation

Required command:

```powershell
python -m unittest discover -s tests -v
```

Expected result:

1. the existing suite remains green before provider-backed quality work is trusted.

## 2. Provider Config Validation

Required checks:

1. OpenAI configuration loads from local secret input without being committed,
2. missing provider config leaves heuristic behavior intact,
3. secrets are not printed in previews or error messages.

## 3. Provider Adapter Validation

Required unit coverage:

1. OpenAI provider can be selected explicitly,
2. accepted skills map to the correct prompt contract,
3. returned outputs are normalized to the existing headline, intro, and excerpt boundaries,
4. unsupported skills are rejected clearly.

## 4. Fallback Regression Validation

Required regression coverage:

1. no-provider behavior still uses the heuristic provider,
2. provider failure falls back cleanly or fails in a controlled way according to policy,
3. `generate_short_intro` still reopens review when content changes,
4. the current micro-skill CLI remains usable without OpenAI configured.

## 5. Acceptance Replay

Required acceptance work:

1. compare heuristic and provider-backed output on a fixed sample set,
2. confirm headline count and quality boundaries,
3. confirm intro bounds remain template-aware,
4. confirm excerpt bounds remain intact,
5. record the results in a Phase 4.6 acceptance batch.

## Definition Of Pass

Phase 4.6 should be considered validated only when:

1. bounded provider-backed quality is measurably better on the chosen sample set,
2. the repo still works with no provider configured,
3. review-state safety and AI usage logging remain correct,
4. no implementation path can silently drift into full-article generation.
