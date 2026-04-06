# Phase 4 Acceptance Batch 1

## Purpose

Record the first real Phase 4 implementation slice.

This batch establishes the initial tracking baseline:

1. on-demand publish-chain snapshots,
2. deterministic source-to-draft-to-blog-to-social-to-Facebook joins,
3. operator-facing publish-chain ledger reporting,
4. no new persisted tracking artifact yet.

## Scope

The accepted scope for this batch is:

1. create the first `tracking_engine` package,
2. define the first `PublishChainSnapshot` contract in code,
3. derive publish-chain history from append-only runtime records,
4. expose the report through a CLI entry point,
5. keep normalization on-demand rather than persisted.

## Commands Run

```powershell
python -m unittest tests.unit.tracking_engine.test_chain_history tests.unit.tracking_engine.test_chain_history_cli -v
python src\cli\summarize_publish_chain_history.py --help
python src\cli\summarize_publish_chain_history.py --json
python -m unittest discover -s tests -v
```

## Result

The initial Phase 4 slice is accepted as the first tracking baseline.

What is now proven:

1. the repo can derive one latest publish-chain snapshot per `blog_publish_id`,
2. publish-chain history can be reconstructed without mutating append-only runtime records,
3. partial chains remain visible,
4. the operator can inspect the chain ledger without reading raw JSONL files by hand,
5. the full repo test suite remained green when the tracking slice was added.

## Important Notes

This batch intentionally does not add:

1. a persisted normalized snapshot file,
2. exception-specific reporting,
3. variant usage summaries,
4. source and template activity summaries,
5. new audit-log record types.

Those remain Phase 4 follow-on work after the first on-demand baseline is stable.
