# Tracking Engine Runbook

## Purpose

This runbook defines the accepted operator path for the current Phase 4 tracking layer.

The goal is to make it easy to:

1. inspect publish-chain history,
2. inspect exception chains,
3. inspect current source/template mix,
4. inspect selected variant usage,
5. record meaningful tracking audits without logging every harmless read.

## Core Rule

Tracking reporting is read-first.

By default:

1. reports are derived on demand,
2. no normalized snapshot artifact is written,
3. no audit record is appended unless the operator explicitly requests it.

## Main Commands

### Publish-chain ledger

```powershell
python src\cli\summarize_publish_chain_history.py
python src\cli\summarize_publish_chain_history.py --json
```

### Exception view

```powershell
python src\cli\summarize_publish_chain_history.py --view exceptions
python src\cli\summarize_publish_chain_history.py --view exceptions --json
```

### Source/template activity view

```powershell
python src\cli\summarize_publish_chain_history.py --view activity
python src\cli\summarize_publish_chain_history.py --view activity --json
```

### Variant usage view

```powershell
python src\cli\summarize_publish_chain_history.py --view variants
python src\cli\summarize_publish_chain_history.py --view variants --json
```

### Combined JSON report

```powershell
python src\cli\summarize_publish_chain_history.py --view all --json
```

## Deliberate Audit Recording

Use audit recording only when the run itself matters:

1. acceptance evidence,
2. milestone review,
3. operator handoff,
4. a meaningful audit checkpoint.

### Record a normalization run

```powershell
python src\cli\summarize_publish_chain_history.py --view all --record-audit
python src\cli\summarize_publish_chain_history.py --view exceptions --record-audit --actor-label operator
```

### Review tracking audit history

```powershell
python src\cli\summarize_tracking_audit.py
python src\cli\summarize_tracking_audit.py --json
```

## Transport Validation Audit Usage

Transport validation audit records should only be created for real execute-mode validation runs.

### WordPress

```powershell
python src\cli\validate_wordpress_transport.py --config-path <wordpress_rest_config.json> --execute --record-audit
```

### Facebook

```powershell
python src\cli\validate_facebook_transport.py --config-path <facebook_graph_config.json> --execute --record-audit
```

Do not add `--record-audit` to harmless preview checks.

## Runtime Artifacts

The current tracking runtime layer uses:

1. append-only upstream runtime records from earlier phases,
2. derived on-demand tracking reports,
3. `data/tracking_audit_records.jsonl` for explicit audit events only.

## What To Check During Normal Use

### Daily or routine checks

1. run the ledger or exception view,
2. confirm there are no unexpected failed or partial chains,
3. inspect activity mix if output balance looks off.

### Milestone checks

1. run `--view all --json`,
2. record a normalization audit event,
3. review the tracking audit summary,
4. attach the result to acceptance documentation if needed.

## What Must Be Avoided

Do not:

1. treat tracking reports as a replacement for the append-only runtime records,
2. record an audit event for every casual read,
3. assume the absence of chains means the reporting code failed,
4. add new audit record types unless a real blind spot is proven.
