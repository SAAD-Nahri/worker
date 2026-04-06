# Phase 2 Gold Set V1

## Purpose

This document defines the fixed Phase 2 gold-set acceptance pack.

Its role is to keep semantic-anchor quality, weak-fit routing, and deterministic draft trust from drifting as Phase 2 continues.

This is now the baseline closeout-oriented acceptance pack for the current Content Engine work.

## Why This Exists

Unit tests already protect structural behavior.

The gold set protects a different layer:

1. whether the draft is actually about the right thing,
2. whether weak-fit content is surfaced honestly,
3. whether the same live failure patterns stay fixed over time,
4. whether the reroute policy behaves consistently.

## Current Scope

The v1 gold set currently includes:

1. clean-fit explainers,
2. named-person food stories,
3. derivative-borderline review cases,
4. recipe-heavy hold cases,
5. roundup/listicle hold cases,
6. trailing-sentiment title hold cases,
7. venue-novelty restaurant-story holds,
8. geographic price-comparison roundup holds,
9. event- or occasion-driven recipe roundup holds,
10. one live blocked duplicate-snapshot control,
11. one fixed blocked thin-text control.

The current pack size is `14` cases.

## Machine-Readable Manifest

The source of truth for the pack lives in:

1. [PHASE_2_GOLD_SET_V1.json](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_GOLD_SET_V1.json)

That file defines:

1. expected template ID,
2. expected subject anchor,
3. expected intro terms,
4. forbidden intro terms,
5. expected quality outcome,
6. required flags,
7. expected routing action,
8. case rationale.

## Current Cases

| case_id | source_item_id | expected quality | expected routing |
|---|---|---|---|
| `pak_mo_clean_fit` | `b3b1fae29b000493955232a2574e3317f0c8e375` | `pass` | `proceed` |
| `costco_container_clean_fit` | `0637ac87046ef3cc65bc45e52155c9f627622329` | `pass` | `proceed` |
| `jacques_pepin_named_person_clean_fit` | `c421b428894b627aa30123361debffe193871270` | `pass` | `proceed` |
| `sopa_negra_review_only` | `4fd1e3a4b14f379e1eebf200ac3864cf05ee296e` | `review_flag` | `review_only` |
| `tsoureki_hold_for_reroute` | `5d1d078eb1ee712d2d76cd96a5578e47b9cf7543` | `review_flag` | `hold_for_reroute` |
| `italian_street_foods_listicle_hold` | `eea895c96f3ba05d3c9d5fda6f1d10ca6316373e` | `review_flag` | `hold_for_reroute` |
| `automated_pay_stations_sentiment_hold` | `78484fac658746a3f991d5733c10da6adfa1e970` | `review_flag` | `hold_for_reroute` |
| `haunted_restaurant_novelty_hold` | `2ec5380afe2daa2578fa3afac82504bd2020dbf8` | `pass` | `hold_for_reroute` |
| `big_arch_price_comparison_hold` | `06b7492c4d8577567bea1dfdaf4610075e947943` | `pass` | `hold_for_reroute` |
| `short_ribs_recipe_title_hold` | `701c8dbb07eb14e7f02152d4514d1677e22b2a17` | `review_flag` | `hold_for_reroute` |
| `tax_day_recipes_listicle_hold` | `16b437bf11c1cc5058c3ff71a716b758442ef116` | `pass` | `hold_for_reroute` |
| `maryland_crab_soup_recipe_heavy_hold` | `1aab755ebf139863a560c0ddd30bbff8dd64aca3` | `review_flag` | `hold_for_reroute` |
| `haunted_restaurant_duplicate_snapshot_reject` | captured live source item | formatting error | `reject_for_v1` |
| `synthetic_insufficient_text_reject` | synthetic control | formatting error | `reject_for_v1` |

## Replay Command

```powershell
python src\cli\replay_phase2_gold_set.py
```

Machine-readable output:

```powershell
python src\cli\replay_phase2_gold_set.py --json
```

## Current Acceptance Standard

The gold set passes only when:

1. every case passes,
2. every subject anchor matches expectation,
3. forbidden intro terms are absent,
4. required flags are present where expected,
5. routing actions match the current weak-fit policy.

## What This Pack Still Does Not Solve

This pack is strong enough to guide the current phase, but it is not the end state.

It still needs:

1. richer expected support-anchor coverage,
2. expansion once Phase 2 template families widen,
3. more clean-fit breadth only if later live intake produces genuinely trustworthy clean-fit families not already represented.

## Rule

If a real live draft failure teaches us something important and repeatable, it should either:

1. be added to this pack,
2. or be explicitly rejected as non-representative.
