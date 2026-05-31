# Lakehouse Operations Runbook

## Purpose
This runbook defines operational procedures for running, validating, and recovering the Lakehouse pipeline in production.

## Scope
- Source standardization (Excel/CSV to standardized CSV)
- ETL execution (`products -> orders -> order_items`)
- Data quality handling (`quarantine/`)
- Catalog/Athena validation
- Archival and reprocessing
- Incident recovery

## Daily Operations
1. Confirm raw arrivals in `raw/orders/`, `raw/order_items/`, `raw/products/`.
2. Trigger or verify Step Functions execution.
3. Check execution completion and task-level status.
4. Validate curated table freshness in Athena.
5. Check `quarantine/` volume and failure alerts.

## Pre-Deployment Checklist
1. All tests pass in CI.
2. Terraform plan reviewed.
3. Required GitHub variables/secrets configured.
4. Glue scripts and state machine definition synced.
5. Rollback reference captured (last known good commit/tag).

## Post-Deployment Validation
1. Run a controlled pipeline execution with known sample input.
2. Confirm ETL order:
   - products job succeeded
   - orders job succeeded
   - order_items job succeeded
3. Confirm state machine reached `Success`.
4. Confirm archive step moved only successfully processed files.
5. Confirm invalid rows are routed to `quarantine/`.

## Athena Validation Queries
Use these checks after successful execution:

```sql
-- no negative order totals
SELECT COUNT(*) AS negative_totals
FROM lakehouse_dwh.orders
WHERE total_amount < 0;
```

```sql
-- referential integrity from order_items to products
SELECT COUNT(*) AS missing_products
FROM lakehouse_dwh.order_items oi
LEFT JOIN lakehouse_dwh.products p
  ON oi.product_id = p.product_id
WHERE p.product_id IS NULL;
```

```sql
-- metadata traceability checks
SELECT
  COUNT(*) AS rows_missing_lineage
FROM lakehouse_dwh.orders
WHERE ingestion_timestamp IS NULL
   OR source_file IS NULL
   OR run_id IS NULL;
```

## Quarantine Handling Procedure
1. Identify quarantine files by dataset/date.
2. Classify root cause:
   - schema mismatch
   - missing required fields
   - invalid timestamps
   - referential integrity failure
3. Correct source records.
4. Re-run only affected dataset flow.
5. Re-validate using Athena checks.
6. Record incident and resolution summary.

## Reprocessing Procedure
1. Locate archived files for the target dataset/date.
2. Restore files into raw path for controlled replay.
3. Trigger Step Functions with a new execution ID.
4. Confirm merge behavior (no duplicate business keys in curated tables).
5. Validate row counts and integrity checks.

## Failure Recovery Procedure
1. Capture failed Step Functions execution ID and failed state.
2. Inspect CloudWatch logs for:
   - Glue job errors
   - Lambda failures
   - Athena validation exceptions
3. Apply fix:
   - data fix
   - job/config fix
   - IAM/permission fix
4. Re-run from a clean new execution.
5. Verify success path and archive completion.

## Backfill Procedure
1. Prepare historical standardized CSVs by date partition.
2. Ingest in controlled batches (date windows).
3. Monitor Glue runtime and quarantine rates.
4. Run validation queries after each batch.
5. Approve batch before moving to next window.

## Observability and Alerts
Monitor:
- Step Functions failed executions
- Glue job failures and duration anomalies
- Quarantine growth spikes
- Athena validation failure events

Minimum alert destinations:
- SNS topic for failures
- Team channel/email notification

## On-Call Handoff Template
- Incident ID:
- Execution ID:
- Affected dataset(s):
- Impact window:
- Root cause:
- Mitigation applied:
- Reprocessing required (Yes/No):
- Final validation result:
- Follow-up actions:
