# Source Engine Runbook

## Purpose

This runbook defines how to operate the current Phase 1 Source Engine baseline in a disciplined way.

It exists to prevent two common mistakes:

1. treating the current intake slice like a throwaway prototype,
2. skipping ahead into article generation or publishing work before intake is stable.

## Current Scope

The current Source Engine baseline is responsible for:

1. loading the active source registry,
2. fetching RSS feeds,
3. extracting feed entries,
4. cleaning and normalizing items,
5. assigning deterministic classification labels,
6. running dedupe checks,
7. optionally fetching article-page bodies for unique items that require them,
8. handling degraded or non-RSS sources through explicit fallback modes,
9. writing append-only runtime records.

It is not yet responsible for:

1. publishing to WordPress,
2. creating Facebook packages,
3. making AI rewrite decisions,
4. deciding winners or promotion candidates,
5. replacing manual source-review judgment.

## Canonical Commands

Run tests:

```powershell
python -m unittest discover -s tests -v
```

Run source intake:

```powershell
python src\cli\run_source_intake.py --limit-per-source 5
```

Run source intake with article-body fetch enabled:

```powershell
python src\cli\run_source_intake.py --limit-per-source 2 --fetch-article-bodies
```

Record a source review decision without changing the registry:

```powershell
python src\cli\review_source_status.py --source-id src_food_republic --reviewed-items 4 --strong-candidates 2 --weak-or-repetitive-items 1
```

Record and apply a source review decision to the registry:

```powershell
python src\cli\review_source_status.py --source-id src_bon_appetit --reviewed-items 4 --strong-candidates 0 --weak-or-repetitive-items 4 --reviewer-notes "Recipe-heavy drift in first review window." --apply-registry-update
```

Summarize current source health:

```powershell
python src\cli\summarize_source_health.py
```

Preview a clean-run reset without changing files:

```powershell
python src\cli\reset_runtime_state.py
```

Archive the current runtime state for a clean local run:

```powershell
python src\cli\reset_runtime_state.py --execute
```

## Main Inputs

1. [data/source_registry.json](C:/Users/Administrator/OneDrive/Documents/co_ma/data/source_registry.json)
2. The live RSS feeds for the active sources

## Main Outputs

1. `data/source_items.jsonl`
2. `data/intake_history.jsonl`
3. `data/dedupe_index.json`
4. `data/source_decisions.jsonl`
5. `data/draft_records.jsonl` when Phase 2 draft persistence is used
6. `data/draft_reviews.jsonl` when Phase 2 draft review persistence is used
7. `data/archive/<timestamp>/...` when runtime reset is executed

## What A Good Run Looks Like

A good run should show:

1. all active sources loading cleanly,
2. feed fetches returning `OK` for most or all active sources,
3. normalized item counts matching the selected per-source cap,
4. dedupe counts that make sense for the age of the runtime state.

## How To Interpret Dedupe Counts

1. Early runs should produce a larger share of `unique` items.
2. Repeated runs against the same active sources will produce more `exact_duplicate` results.
3. High duplicate counts on later runs are normal if the registry and dedupe memory are stable.
4. A sudden collapse in total items or repeated fetch errors is a source-health problem, not a content-quality problem.

## Article-Body Fetch Rules

1. Article-body fetching is opt-in, not automatic.
2. It should only be used for unique items from sources that require body extraction.
3. It must stay inside the approved source domain boundary.
4. If extraction fails or is too weak, the item falls back to feed-derived text and the failure is recorded in item flags and run history.
5. This step exists to improve structured downstream formatting, not to justify broad crawling.

## Source Fallback Rules

1. `rss_native` and `rss_plus_fetch` sources are the normal auto-intake path.
2. If an RSS-first source is missing a feed or returns a broken feed, it is treated as `degraded`, not silently broadened into crawler behavior.
3. `manual_seed` and `selective_scrape` sources stay in manual mode in Phase 1.
4. A degraded or manual-only source should surface clearly in run history and source-health reporting.
5. The fallback path for degraded or non-RSS sources is operator review, not automatic crawl escalation.

## Locked Phase 1 Rule

For Phase 1, article-body extraction stays as an opt-in intake-time path for unique items.

It is not the default for every run, and it is not being moved to a later engine yet.

## Locked Review Rule

For Phase 1, source-review decisions are always recorded, but registry changes remain operator-applied.

The system may recommend a new status, but it does not silently change the live source set by default.

## Runtime Reset Rule

For Phase 1, runtime logging stays append-only by default.

If a clean local run is needed, use the explicit archive-first reset workflow instead of deleting files ad hoc.

That runtime reset now covers both Phase 1 and current Phase 2 runtime artifacts.

## Operator Routine For Phase 1

1. Keep the active registry small and intentional.
2. Run intake against the current source set.
3. Inspect run history for fetch failures or source drift.
4. Use the source health summary to see which sources need review attention.
5. Review normalized candidates in the logs and live execution docs.
6. Record source review decisions once a source has enough evidence.
7. Apply registry updates only when the operator wants the live source set to change.
8. Use runtime reset only when a clean local run is genuinely needed.

## Remaining Phase 1 Priorities

1. Keep this slice deterministic and stable before any Content Engine work begins.
