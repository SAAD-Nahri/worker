# Phase 4.8 Acceptance Batch 1

## Purpose

Record the first executable runtime-operations slice for deployment, backup, and recovery.

## Work Completed

1. Added `python src\cli\create_runtime_backup.py` for runtime backup bundles.
2. Added `python src\cli\restore_runtime_backup.py` for safe restore previews and controlled restore runs.
3. Kept runtime backup scope centered on `data/` by default, with optional `config/*.local.json` inclusion only when explicitly requested.
4. Added example `systemd` service and timer files for:
   1. recurring source intake,
   2. daily JSON runtime reports,
   3. daily runtime backups.
5. Updated deployment, data, and execution docs so the new runtime tooling is part of the documented operating model.

## Why This Matters

The repo already had runtime policy and hosted Operator API guidance, but the remaining Phase 4.8 gap was that backup and recurring-job behavior still depended too much on prose.

This batch makes the runtime model more concrete:

1. backups can now be created from a dedicated CLI,
2. restores can be previewed safely before writing files,
3. the production scheduler examples now cover more than the always-on Operator API service.

## Validation

Focused validation:

1. `python -m unittest tests.unit.runtime_ops.test_backup -v`

Repo baseline:

1. `python -m unittest discover -s tests -v`

## Result

The Python baseline is green at `251` tests passing.

The runtime deployment baseline is now implemented enough to support real host rehearsal work.

The honest remaining Phase 4.8 gaps are still external and rehearsal-oriented:

1. cold-start deployment still needs to be performed on the chosen host,
2. backup and recovery still need one real drill against live-style runtime data,
3. formal Phase 4.8 closeout still depends on those rehearsals, not just the repo implementation.
