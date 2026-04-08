# Phase 4.6 Validation Plan

## Purpose

This document defines how the AI-assisted content-quality phase should be validated.

The focus is bounded quality improvement with controlled failure behavior, visible provenance, and no loss of deterministic safety.

## Validation Layers

Phase 4.6 validation has six layers:

1. repo baseline validation,
2. provider-config validation,
3. provider-adapter validation,
4. regression validation for no-provider fallback,
5. social refinement validation,
6. bounded acceptance replay.

## 1. Repo Baseline Validation

Required command:

```powershell
python -m unittest discover -s tests -v
```

Expected result:

1. the existing suite remains green before provider-backed quality work is trusted.

## 2. Provider Config Validation

Required checks:

1. `OPENAI_API_KEY` overrides file `api_key`,
2. `model` and `timeout_seconds` can load from the ignored local config file,
3. invalid JSON and invalid timeout values fail explicitly,
4. missing provider config leaves heuristic behavior intact,
5. secrets are not printed in previews or error messages.

## 3. Provider Adapter Validation

Required unit coverage:

1. OpenAI provider can be selected explicitly,
2. accepted skills map to the correct prompt contract,
3. returned outputs are normalized to the existing headline, intro, and excerpt boundaries,
4. weak or invalid output retries once before fallback,
5. unsupported skills are still rejected clearly.

## 4. Fallback Regression Validation

Required regression coverage:

1. no-provider behavior still uses the heuristic provider,
2. provider failure falls back cleanly or fails in a controlled way according to policy,
3. `generate_short_intro` still reopens review when content changes,
4. the current micro-skill CLI remains usable without OpenAI configured,
5. the CLI reports the requested provider, effective provider, and fallback reason without exposing secrets.

## 5. Social Refinement Validation

Required checks:

1. `prepare_facebook_package` remains deterministic and unchanged,
2. `refine_social_package.py --provider openai` only appends variant options,
3. current selected package text stays unchanged until explicit variant selection,
4. `ai_assistance_log` entries are appended for social refinement,
5. selecting an OpenAI-generated variant reopens social review through the existing guarded path,
6. operator API and plugin detail views expose AI provenance as read-only context.

## 6. Acceptance Replay

Required acceptance work:

1. compare heuristic and provider-backed output on a fixed sample set,
2. confirm headline count and quality boundaries,
3. confirm intro bounds remain template-aware,
4. confirm excerpt bounds remain intact,
5. confirm social refinement variants stay within package bounds,
6. record the results in a Phase 4.6 acceptance batch.

## Definition Of Pass

Phase 4.6 should be considered validated only when:

1. bounded provider-backed quality is measurably better on the chosen sample set,
2. the repo still works with no provider configured,
3. review-state safety and AI usage logging remain correct,
4. social-package refinement stays manual and review-safe,
5. no implementation path can silently drift into full-article generation or transport automation.
