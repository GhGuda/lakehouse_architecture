# Lakehouse Architecture

End-to-end AWS Lakehouse pipeline for e-commerce transaction data using Amazon S3, AWS Glue (PySpark), Delta Lake, AWS Step Functions, AWS Glue Data Catalog, and Amazon Athena.

## Objective
Build a reliable analytics pipeline that ingests raw commerce data, enforces data quality, produces curated Delta tables, and makes trusted datasets queryable in Athena.

## Source Data
- `Data/orders_apr_2025.xlsx`
- `Data/order_items_apr_2025.xlsx`
- `Data/products.csv`

## End-to-End Flow
1. Standardize inputs:
   - Convert Excel worksheets to per-day CSV files.
   - Keep incoming CSV files as-is.
2. Land standardized files in S3 raw zone (`raw/`).
3. Orchestrate ETL with Step Functions in dependency order:
   - `products` -> `orders` -> `order_items`
4. Process with Glue + Spark:
   - schema enforcement
   - validation and rejection routing
   - deduplication
   - Delta merge/upsert
5. Write rejected records to `quarantine/`.
6. Write curated Delta tables to `processed/`.
7. Register/update tables in Glue Data Catalog.
8. Validate and query curated data with Athena.
9. Archive successfully processed raw files to `archived/`.

## Lakehouse Zones
- `raw/`: standardized CSV inputs
- `processed/`: curated Delta tables
- `quarantine/`: invalid/rejected records
- `archived/`: successfully processed raw files
- `athena-results/`: Athena query outputs

## Core Components
- **Amazon S3**: storage for all data zones
- **AWS Glue + PySpark**: ETL processing
- **Delta Lake**: ACID tables and merge semantics
- **AWS Step Functions**: workflow orchestration and retries
- **AWS Glue Data Catalog**: metadata layer
- **Amazon Athena**: SQL query and validation
- **GitHub Actions**: CI/CD for test and deployment
- **CloudWatch**: logs, metrics, alarms

## Local Setup
```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS/Linux:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Repository Structure
```text
.
|-- Data/
|-- docs/
|-- glue_jobs/
|   `-- utils/
|-- stepfunctions/
|-- iac/
|-- tests/
|   `-- fixtures/
|-- .github/
|   `-- workflows/
|-- requirements.txt
|-- README.md
`-- status.md
```

## Data Quality Principles
- Enforce required fields and expected types.
- Reject invalid records to quarantine instead of silent drops.
- Preserve idempotency and deterministic merges.
- Apply referential checks where applicable (for example `order_items.product_id` against `products.product_id`).

## Operations and Reliability
- Retry transient ETL failures with backoff.
- Log structured execution metrics (read/written/rejected counts, durations).
- Monitor Glue jobs and Step Functions with CloudWatch alarms.
- Keep reprocessing and recovery steps documented in project runbooks.

## Project Documentation
- `docs/plan/plan.md`
- `docs/architecture.png`
- `docs/Building a Lakehouse Using PySpark Delta Tables & S3.pdf`
- `status.md` (stage progress and handoff tracker)

## CI/CD Configuration
GitHub Actions workflow: `.github/workflows/ci-cd.yml`

Required GitHub repository variables:
- `AWS_REGION`
- `LAKEHOUSE_BUCKET_NAME`
- `DETECT_NEW_FILES_LAMBDA_ARN`
- `CATALOG_UPDATE_LAMBDA_ARN`
- `ATHENA_VALIDATION_LAMBDA_ARN`
- `ARCHIVE_FILES_LAMBDA_ARN`
- `FAILURE_NOTIFICATIONS_TOPIC_ARN`

Required GitHub repository secret:
- `AWS_ROLE_TO_ASSUME` (OIDC assumable IAM role ARN)
