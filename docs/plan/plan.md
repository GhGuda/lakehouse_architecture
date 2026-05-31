# Lakehouse Architecture for E-Commerce Transactions – Revised Implementation Plan

## 1. Project Overview
This document outlines the end-to-end implementation plan for a production-grade Lakehouse on AWS for e-commerce transactional data. The solution ingests source files for **orders**, **products**, and **order items**, standardizes them into CSV where needed, processes them using **AWS Glue + Spark with Delta Lake**, stores curated Delta tables in Amazon S3, and exposes them through the **AWS Glue Data Catalog** and **Amazon Athena**.

The ETL lifecycle is orchestrated with **AWS Step Functions**, and deployment/testing is automated with **GitHub Actions**.

This revised plan keeps the strong parts of the original design while making the following practical adjustments:
- explicitly supports the actual source formats (**Excel workbooks and CSV files**)
- standardizes Excel sheets into CSV before core ETL processing
- uses a **dependency-aware orchestration flow** instead of fully parallel execution
- clarifies Delta registration for Glue Catalog and Athena
- makes archiving ownership explicit
- preserves the production-grade aspects: validation, deduplication, monitoring, testing, and CI/CD

---

## 2. Source File Handling and Standardization

### 2.1 Actual Source Files
The available source files are:
- `orders_apr_2025.xlsx`
- `order_items_apr_2025.xlsx`
- `products.csv`

The Excel files contain multiple daily worksheets. Because the project brief expects ingestion from **CSV files into the S3 raw zone**, the plan standardizes incoming Excel sheets into CSV files before the core Glue/Delta pipeline processes them.

### 2.2 Standardization Rule
- **CSV files** are uploaded directly into the raw zone.
- **Excel workbooks** are converted **sheet-by-sheet** into individual CSV files.
- Each worksheet date is preserved in the output filename.
- Logical ordering is preserved through filenames, dates, and timestamps rather than physical row order.

### 2.3 Standardized Output Examples
```text
orders_apr_2025.xlsx / sheet 2025-04-01
  -> raw/orders/orders_2025-04-01.csv

orders_apr_2025.xlsx / sheet 2025-04-02
  -> raw/orders/orders_2025-04-02.csv

order_items_apr_2025.xlsx / sheet 2025-04-01
  -> raw/order_items/order_items_2025-04-01.csv

products.csv
  -> raw/products/products.csv
```

### 2.4 Where Conversion Happens
A lightweight **pre-ingestion standardization step** converts Excel sheets into CSV before the main ETL jobs. This can be implemented in one of two acceptable ways:
1. **Recommended for this project:** convert locally or in a lightweight script before upload to the raw zone.
2. **Optional automated variant:** run a small preprocessing job that reads Excel and writes standardized CSVs into the raw zone.

For the main production plan, the **raw zone is treated as standardized CSV input**, so all downstream Glue jobs operate consistently.

---

## 3. Architecture Summary
The architecture follows this flow:
1. Source files arrive as **Excel or CSV**.
2. Excel worksheets are standardized into CSV files.
3. Standardized CSVs are stored in the **S3 raw zone**.
4. **AWS Step Functions** orchestrates the ETL sequence.
5. **AWS Glue + Spark** validates, cleans, deduplicates, and merges data into **Delta Lake tables** in the processed zone.
6. Invalid records are written to **quarantine**.
7. Successfully processed raw files are moved to **archived/**.
8. Delta tables are registered/updated in the **Glue Data Catalog**.
9. **Athena** queries the curated tables.
10. **GitHub Actions** runs tests and deploys the solution on changes to `main`.

---

## 4. High-Level Architecture Components

### Core Services Used
| Service | Purpose |
|---|---|
| Amazon S3 | Raw, processed, archived, quarantine, and Athena query result storage |
| AWS Glue + Spark | Distributed ETL processing |
| Delta Lake | ACID-compliant table format on top of S3 |
| AWS Step Functions | ETL orchestration |
| AWS Glue Data Catalog | Metadata layer for Glue + Athena |
| Amazon Athena | Query engine for downstream analytics |
| GitHub Actions | CI/CD pipeline for tests and deployment |
| Amazon CloudWatch | Monitoring, logs, alarms |

---

## 5. S3 Folder Structure
```text
s3://ecommerce-lakehouse/
│
├── raw/                                    # Standardized CSV input
│   ├── orders/
│   │   ├── orders_2025-04-01.csv
│   │   ├── orders_2025-04-02.csv
│   │   └── ...
│   ├── products/
│   │   └── products.csv
│   └── order_items/
│       ├── order_items_2025-04-01.csv
│       ├── order_items_2025-04-02.csv
│       └── ...
│
├── processed/                              # Delta Lake tables
│   ├── orders/
│   │   ├── _delta_log/
│   │   └── date=YYYY-MM-DD/
│   ├── products/
│   │   └── _delta_log/
│   └── order_items/
│       ├── _delta_log/
│       └── order_date=YYYY-MM-DD/
│
├── archived/                               # Successfully processed raw files
│   ├── orders/
│   ├── products/
│   └── order_items/
│
├── quarantine/                             # Rejected / invalid rows
│   ├── orders/
│   ├── products/
│   └── order_items/
│
└── athena-results/                         # Athena query output
```

---

## 6. Delta Lake Table Schemas and Validation Rules

### 6.1 Orders Table
```sql
CREATE TABLE lakehouse_dwh.orders (
    order_num        INT,
    order_id         INT         NOT NULL,
    user_id          INT         NOT NULL,
    order_timestamp  TIMESTAMP   NOT NULL,
    total_amount     DECIMAL(10,2),
    date             DATE
)
USING DELTA
PARTITIONED BY (date)
LOCATION 's3://ecommerce-lakehouse/processed/orders/';
```

**Validation rules**
- `order_id IS NOT NULL`
- `user_id IS NOT NULL`
- `order_timestamp` must be convertible to timestamp
- `total_amount >= 0`
- duplicate `order_id` across files -> keep latest using Delta `MERGE`
- invalid rows -> write to `quarantine/orders/`

**Partitioning decision**
- Partition by `date` for analytical filtering and improved performance.

### 6.2 Products Table
```sql
CREATE TABLE lakehouse_dwh.products (
    product_id      INT         NOT NULL,
    department_id   INT,
    department      STRING,
    product_name    STRING
)
USING DELTA
LOCATION 's3://ecommerce-lakehouse/processed/products/';
```

**Validation rules**
- `product_id IS NOT NULL`
- log if `department` is empty
- deduplicate on `product_id`

**Partitioning decision**
- The `products` table is intentionally **not partitioned**.
- This is a relatively small dimension table, so partitioning would add overhead and increase small-file fragmentation without meaningful query benefit.

### 6.3 Order Items Table
```sql
CREATE TABLE lakehouse_dwh.order_items (
    id                       INT         NOT NULL,
    order_id                 INT         NOT NULL,
    user_id                  INT,
    days_since_prior_order   INT,
    product_id               INT         NOT NULL,
    add_to_cart_order        INT,
    reordered                BOOLEAN,
    order_timestamp          TIMESTAMP   NOT NULL,
    order_date               DATE
)
USING DELTA
PARTITIONED BY (order_date)
LOCATION 's3://ecommerce-lakehouse/processed/order_items/';
```

**Validation rules**
- `id IS NOT NULL`
- `order_id IS NOT NULL`
- `product_id IS NOT NULL`
- `order_timestamp` must be valid
- `add_to_cart_order >= 1` when present
- deduplicate on `id`
- enforce referential checks against `products.product_id`
- optionally validate `order_id` existence in `orders`
- invalid rows -> write to `quarantine/order_items/`

**Partitioning decision**
- Partition by derived `order_date` to support date-based analytics and reduce scan volume.

---

## 7. Glue ETL Job Design
All ETL jobs are written in **PySpark** with Delta Lake support. The jobs are modular, reusable, and idempotent.

### 7.1 Shared Utilities
Create `glue_jobs/utils/delta_utils.py` with reusable functions such as:
- `read_with_schema(spark, path, schema)`
- `validate_dataframe(df, rules)`
- `write_rejected_records(df, path)`
- `merge_delta_table(df, delta_path, merge_key, partition_cols)`
- `collect_processed_files(...)`

### 7.2 `orders_etl.py`
Steps:
1. Read new standardized CSV files from `raw/orders/`.
2. Apply schema enforcement.
3. Validate required columns and data quality rules.
4. Convert `order_timestamp` to timestamp and derive `date`.
5. Add metadata columns such as `ingestion_timestamp` and `source_file`.
6. Merge into Delta table on `order_id`.
7. Return success status and processed file list to the orchestrator.

### 7.3 `products_etl.py`
Steps:
1. Read `raw/products/products.csv`.
2. Validate `product_id` and deduplicate.
3. Merge or overwrite the Delta dimension table.
4. Return success status and processed file list.

### 7.4 `order_items_etl.py`
Steps:
1. Read new standardized CSV files from `raw/order_items/`.
2. Apply schema enforcement and validation.
3. Convert `order_timestamp` and derive `order_date`.
4. Validate `product_id` against the curated `products` table.
5. Optionally validate `order_id` against the curated `orders` table.
6. Merge into Delta table on `id`.
7. Return success status and processed file list.

### 7.5 Optimization
- `OPTIMIZE` and `VACUUM` can be run as scheduled maintenance jobs.
- Avoid over-partitioning small datasets.
- Consider compaction where frequent small files occur.

---

## 8. Orchestration with AWS Step Functions

### 8.1 Design Principle
The original plan used fully parallel ETL branches. This revision changes that to a **dependency-aware flow** because `order_items` depends on `products`, and optionally on `orders`, for referential checks.

### 8.2 Recommended State Machine Flow
```text
Start
 -> Detect new standardized raw files
 -> Run products_etl (if products changed, otherwise skip)
 -> Run orders_etl
 -> Run order_items_etl
 -> Update Glue Catalog / partitions
 -> Run Athena validation query
 -> Archive processed raw files
 -> Success
```

### 8.3 Failure Handling
The state machine should include:
- retries for transient Glue failures (e.g., 3 attempts with exponential backoff)
- timeout handling per Glue job
- failure branch to CloudWatch Logs and optional SNS alerting
- branching for skip/no-new-file scenarios

### 8.4 Event Trigger
**Recommended trigger:**
- S3 Put event -> EventBridge -> Step Functions
- filter on the `raw/` prefix for standardized CSV arrivals

**Optional fallback:**
- scheduled Step Functions execution (e.g., hourly)

### 8.5 Archiving Ownership
Archiving is owned by **Step Functions** for clarity and control.
- Each Glue job returns the list of successfully processed files.
- Step Functions moves those files from `raw/` to `archived/` only after the corresponding processing succeeds.
- Failed files remain in place or are only partially handled through quarantine for row-level failures.

---

## 9. Glue Data Catalog and Athena
After successful writes to Delta Lake:
1. Register or update each table in the **Glue Data Catalog**.
2. Ensure the table definitions point to the Delta table locations in `processed/`.
3. Refresh metadata/partitions as required.
4. Use **Athena** for validation and downstream analytics.

### Notes
- A Glue Crawler may be used if desired, but table registration/update logic should explicitly support Delta table metadata.
- The important outcome is that Athena can query the curated Delta tables correctly via the Glue Catalog.

### Example Athena Validation Query
```sql
SELECT COUNT(*) AS invalid_total_amounts
FROM lakehouse_dwh.orders
WHERE total_amount < 0;
```
If the result is greater than 0, the workflow can branch to failure handling.

---

## 10. CI/CD with GitHub Actions

### 10.1 Repository Structure
```text
.github/
└── workflows/
    └── deploy.yml
glue_jobs/
├── orders_etl.py
├── products_etl.py
├── order_items_etl.py
└── utils/
    └── delta_utils.py
stepfunctions/
└── state_machine.json
iac/
├── glue_role_policy.json
├── stepfunctions_role_policy.json
└── s3_buckets.tf
tests/
├── test_validation.py
├── test_delta_merge.py
└── fixtures/
README.md
plan.md
```

### 10.2 CI/CD Pipeline
Trigger scope:
- push to `main`
- optionally PR validation before merge

Pipeline stages:
1. **test**
   - run `pytest`
   - run linting (e.g., `flake8`)
2. **deploy**
   - sync Glue scripts to S3
   - create/update Glue jobs
   - deploy Step Function definition
   - optionally deploy IaC resources
3. **notify**
   - optional Slack or email notification

### 10.3 Security Improvement
Use **GitHub Actions OIDC** to assume an AWS deployment role instead of storing long-lived AWS access keys where possible.

---

## 11. Monitoring and Alerting
Use **CloudWatch** for operational observability.

### Dashboard Suggestions
- Glue job durations
- Step Functions execution status
- records processed / rejected per dataset
- quarantine counts
- S3 storage growth

### Example Alarms
| Alarm | Condition | Action |
|---|---|---|
| GlueJobFailure | Any Glue job fails | SNS / Slack |
| HighQuarantineRate | Quarantine records exceed threshold | SNS / Slack |
| StepFunctionStuck | Execution exceeds expected duration | SNS |
| DataQualityFailure | Athena validation query fails | SNS |

### Structured Logging Fields
```json
{
  "job_name": "orders_etl",
  "execution_id": "jr_abc123",
  "records_read": 5000,
  "records_written": 4980,
  "records_rejected": 20,
  "start_time": "2025-04-15T10:00:00Z",
  "end_time": "2025-04-15T10:05:30Z"
}
```

---

## 12. Data Quality and Testing Strategy

### Unit Tests
- validation functions
- Delta merge logic
- schema enforcement
- archive/move utility logic

### Integration Tests
- deploy to a dev environment
- ingest a sample standardized CSV batch
- verify curated Delta outputs, quarantine paths, and Athena access

### Production Checks
- post-load Athena validation queries
- row count sanity checks
- duplicate detection checks
- referential integrity checks for `product_id` and optionally `order_id`

---

## 13. End-to-End Execution Flow
```text
1. Developer pushes code changes -> GitHub Actions runs tests and deploys updates.
2. Source files are prepared:
   - Excel worksheets are converted into standardized CSV files.
   - Existing CSV files are kept as-is.
3. Standardized CSV files are uploaded to s3://ecommerce-lakehouse/raw/...
4. S3 event triggers EventBridge -> starts Step Functions.
5. Step Functions runs:
   - products_etl
   - orders_etl
   - order_items_etl
6. Glue jobs validate, clean, deduplicate, and merge data into Delta tables.
7. Rejected rows are written to quarantine/.
8. Step Functions updates the Glue Catalog and runs Athena validation checks.
9. On success, Step Functions archives the processed raw CSV files.
10. Business users query curated data through Athena.
```

---

## 14. Deliverables Summary
| Component | Status | Notes |
|---|---|---|
| S3 raw / processed / archived / quarantine zones | Planned | included |
| Excel-to-CSV standardization | Added | revised to match actual files |
| Delta schemas and validation rules | Designed | included |
| Glue ETL scripts | To be implemented | modular PySpark |
| Step Functions orchestration | Revised | dependency-aware |
| Glue Catalog + Athena integration | Clarified | included |
| GitHub Actions CI/CD | Designed | main branch scope |
| Monitoring & alerts | Planned | CloudWatch |
| Testing strategy | Planned | unit + integration |

---

## 15. Next Steps
1. Finalize the standardization approach for Excel -> CSV.
2. Create the S3 bucket structure.
3. Implement Glue ETL scripts and shared utilities.
4. Define the Step Functions state machine JSON.
5. Register Delta tables in the Glue Catalog.
6. Configure GitHub Actions for test and deployment.
7. Run an end-to-end dry run using the provided April 2025 datasets.
8. Add operational runbooks for reprocessing, quarantine handling, and failure recovery.

---

## 16. Final Recommendation
This revised plan remains faithful to the original project requirements while better matching the real input files and strengthening end-to-end execution. The main design choices are:
- standardize Excel sheets into CSV before core ingestion
- preserve logical ordering by filenames and timestamps, not row order
- keep the strong validation, Delta, and CI/CD design
- use dependency-aware orchestration
- make Athena/Glue Catalog integration and archiving responsibilities explicit

