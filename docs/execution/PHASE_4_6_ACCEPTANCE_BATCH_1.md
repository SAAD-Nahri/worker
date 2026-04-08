# Phase 4.6 Acceptance Batch 1

## Purpose

Record the first implementation and validation batch for the optional OpenAI-backed quality layer.

## Work Completed

1. Added an optional OpenAI config loader with `OPENAI_API_KEY` precedence over `config/openai_provider_config.local.json`.
2. Added an OpenAI-backed draft micro-skill provider using the official Python SDK and the Responses API behind the existing provider seam.
3. Preserved deterministic and heuristic behavior by keeping `apply_micro_skills(...)` authoritative for normalization, fallback, and review reopening.
4. Added manual draft CLI selection through `python src\cli\apply_draft_micro_skills.py ... --provider openai`.
5. Added manual Facebook package refinement through `python src\cli\refine_social_package.py --social-package-id <id> --provider openai`.
6. Kept Facebook package preparation deterministic and unchanged.
7. Added review-visible AI provenance on draft and social package records and surfaced that metadata through the operator API and WordPress approval UI detail views.

## Quality Comparison

This batch compared the heuristic baseline with bounded provider-backed outputs using fixed test fixtures and injected provider responses.

Observed comparison:

1. heuristic mode still produces valid bounded headline, intro, and excerpt results with no OpenAI config,
2. provider-backed mode routes through the explicit prompt contracts and can return cleaner alternative wording while staying inside the same bounds,
3. provider-backed social refinement generates full package bundles instead of field-by-field free edits, which keeps review safer than ad hoc manual rewriting.

Important limitation:

1. this acceptance batch does not claim a live paid OpenAI quality win on production content because no live operator API key was used during automated validation.

## Fallback Evidence

Fallback coverage in this batch proved:

1. missing or invalid OpenAI config falls back safely on the draft CLI,
2. weak provider output falls back to heuristic draft output,
3. missing OpenAI config on the social refinement CLI reports a safe fallback reason without mutating the selected package,
4. selecting an OpenAI-generated social variant still reopens review through the existing guarded variant-selection path.

## Cost Notes

Cost control remains intentionally narrow in this implementation:

1. provider usage is manual opt-in only,
2. draft quality calls are limited to bounded micro-skills rather than full-article generation,
3. each provider-backed draft task retries at most once,
4. social refinement requests at most `1` to `2` package variants and retries at most once,
5. no background jobs, autopilot flows, or approval-UI buttons call OpenAI in this phase.

## Validation

Focused validation:

1. `python -m unittest tests.unit.content_engine.test_openai_provider tests.unit.content_engine.test_micro_skill_cli tests.unit.content_engine.test_micro_skills tests.unit.distribution_engine.test_social_refinement tests.unit.operator_api.test_app -v`

Repo baseline:

1. `python -m unittest discover -s tests -v`

## Result

The Python baseline is green at `246` tests passing.

This batch is sufficient to treat the optional Phase 4.6 quality layer as implemented and review-safe.

The honest remaining limitation is live provider evaluation:

1. real-key editorial comparison and spend observation are still future operator validation work,
2. provider-backed generation remains intentionally outside the WordPress admin UI in this phase,
3. formal Phase 4.6 closeout still depends on later phase-governance review, not just implementation.
