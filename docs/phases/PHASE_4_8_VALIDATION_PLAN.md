# Phase 4.8 Validation Plan

## Purpose

This plan defines how to validate that the chosen runtime and deployment model is good enough for the solo-operator business.

The validation target is not "fancy infrastructure." It is:

1. the system can be deployed cleanly,
2. recurring jobs can run predictably,
3. runtime data can be backed up,
4. the operator can recover from failure without guesswork.

## Validation Questions

Phase 4.8 should answer:

1. can a new host be prepared from the documented runbook,
2. can the repo be updated without silent runtime drift,
3. can recurring jobs be scheduled using the chosen scheduler,
4. can runtime state be backed up and restored,
5. is the operating model simple enough for one person to maintain.

## Required Validation Baseline

### 1. Repository baseline

The codebase and docs baseline should remain green:

```powershell
python -m unittest discover -s tests -v
```

### 2. Activation baseline

The runtime model must inherit the accepted live-activation baseline:

```powershell
python src\cli\summarize_system_activation.py --json
python src\cli\summarize_distribution_health.py --json
python src\cli\summarize_publish_chain_history.py --view all --json
python src\cli\summarize_tracking_audit.py --json
```

### 3. Deployment rehearsal

At minimum, the operator should rehearse:

1. a first deployment to the chosen production host,
2. an update deployment on the same host,
3. a restart of recurring scheduled jobs.

### 4. Backup and recovery rehearsal

At minimum, the operator should rehearse:

1. backing up runtime data,
2. restoring runtime data to a clean working copy,
3. rerunning health and history commands after restore.

### 5. Scheduler rehearsal

The chosen scheduler should prove:

1. recurring intake can run on schedule,
2. recurring reporting can run on schedule,
3. recurring backup can run on schedule,
4. failures surface clearly in logs or journal output.

## Acceptance Evidence

Before Phase 4.8 closes, the repo should contain:

1. a closeout review,
2. explicit evidence that the production model was rehearsed,
3. explicit evidence that backup and recovery were rehearsed,
4. an updated Phase 5 gate showing runtime questions are no longer open.

## Failure Conditions

Phase 4.8 should remain open if any of the following are still true:

1. the system only works from the developer workstation,
2. the production scheduler is still undecided,
3. backup location or restore steps are still vague,
4. deployment still depends on undocumented manual intuition,
5. Phase 5 would need to answer runtime questions before starting decision logic.
