# Project Status

## Project
- Name: Lakehouse Architecture
- Repository target: `GhGuda/lakehouse_architecture`
- Working model: Incremental stage-based delivery with testing and clean PRs

## Stage Tracker

### Stage 01 - Project Scaffold
- Date: 2026-05-31
- Branch: `feat/stage-01-scaffold`
- Status: Completed
- Scope:
  - Create baseline project structure for ETL, orchestration, IaC, tests, and CI folders.
  - Add top-level project `README.md`.
  - Add environment dependency baseline (`requirements.txt`).
  - Initialize `status.md` for transparent handoff.
- Delivered:
  - Folder scaffold created:
    - `glue_jobs/`
    - `glue_jobs/utils/`
    - `stepfunctions/`
    - `iac/`
    - `tests/`
    - `tests/fixtures/`
    - `.github/workflows/`
  - `README.md` created and refined to end-to-end project documentation.
  - `requirements.txt` created for local setup baseline.
  - `status.md` created.
- Testing:
  - Structural validation by directory/file existence checks.
  - Documentation and dependency file presence verified.
- Risks/Notes:
  - None.
- Next:
  - Stage 02 implementation.

### Stage 02 - Excel to CSV Standardization
- Date: 2026-05-31
- Branch: `feat/stage-02-standardize-excel-to-csv`
- Status: Completed
- Scope:
  - Build a reusable utility to standardize source files into CSV outputs.
  - Ensure Excel workbooks are converted sheet-by-sheet with date-preserving file names.
  - Avoid hardcoded file names by discovering `.xlsx` and `.csv` inputs dynamically from `Data/`.
  - Add validation, error handling, and automated tests.
- Delivered:
  - Added script: `scripts/standardize_raw_inputs.py`
    - Discovers input files dynamically in `Data/` (`.xlsx`, `.csv`).
    - Converts Excel workbooks into per-sheet CSV files using sanitized sheet names.
    - Copies CSV inputs into dataset-scoped standardized paths.
    - Includes custom `StandardizationError` handling and source validation.
    - Exposes reusable functions only (no CLI `main` entrypoint).
  - Added tests: `tests/test_standardize_raw_inputs.py`
  - Added `.gitignore` entries for `.venv`, caches, and generated `standardized/` outputs.
- Testing:
  - Command: `python -m pytest -q tests/test_standardize_raw_inputs.py`
  - Result: `4 passed`
- Risks/Notes:
  - Dataset naming is inferred from source file stems; non-standard naming patterns should be reviewed before production.
- Next:
  - Stage 03 shared ETL utilities.

### Stage 03 - Shared ETL Utilities
- Date: 2026-05-31
- Branch: `feat/stage-03-etl-utils`
- Status: Completed
- Scope:
  - Add reusable shared ETL utility functions for upcoming dataset-specific Glue jobs.
  - Keep utilities focused on validation, record quality split, deduplication, and processed-file metadata handoff.
- Delivered:
  - Added utility module: `glue_jobs/utils/delta_utils.py`
    - `validate_required_columns(...)`
    - `split_valid_invalid_records(...)`
    - `deduplicate_by_key(...)`
    - `build_processed_file_manifest(...)`
    - `DataValidationError` and `ValidationRule`
  - Added tests: `tests/test_delta_utils.py`
- Testing:
  - Command: `python -m pytest -q tests/test_delta_utils.py tests/test_standardize_raw_inputs.py`
  - Result: `8 passed`
- Risks/Notes:
  - Utilities are pandas-based for deterministic local testing; Spark-specific integration wrappers will be added with dataset ETL jobs in Stage 04.
- Next:
  - Stage 04 dataset ETL jobs (`products`, `orders`, `order_items`).

### Stage 04 - Dataset ETL Jobs
- Date: 2026-05-31
- Branch: `feat/stage-04-dataset-etl-jobs`
- Status: Completed (local)
- Scope:
  - Implement dataset-level ETL modules for `products`, `orders`, and `order_items`.
  - Reuse Stage 03 utilities for validation, quality split, deduplication, and manifest output.
- Delivered:
  - Added `glue_jobs/products_etl.py` with `run_products_etl(...)`.
  - Added `glue_jobs/orders_etl.py` with `run_orders_etl(...)`.
  - Added `glue_jobs/order_items_etl.py` with `run_order_items_etl(...)`.
  - Added tests: `tests/test_dataset_etl_jobs.py`.
- Testing:
  - Command: `python -m pytest -q tests/test_delta_utils.py tests/test_dataset_etl_jobs.py tests/test_standardize_raw_inputs.py`
  - Result: `11 passed`
- Risks/Notes:
  - Current ETL implementations are pandas-based local job logic; Spark/Delta write integration and Glue runtime wiring will be added in upcoming orchestration/infrastructure stages.
- Next:
  - Stage 05 Step Functions orchestration.

### Stage 05 - Step Functions Orchestration
- Date: 2026-05-31
- Branch: `feat/stage-05-stepfunctions-orchestration`
- Status: Completed (local)
- Scope:
  - Implement a dependency-aware Step Functions state machine for end-to-end ETL orchestration.
  - Include retry, failure routing, validation gate, and archive-on-success flow.
- Delivered:
  - Added state machine definition: `stepfunctions/state_machine.json`
    - Flow: detect -> products -> orders -> order_items -> catalog update -> Athena validation -> archive -> success
    - Failure path via SNS notify -> fail state
    - Retries configured on task states
  - Added orchestration test: `tests/test_state_machine.py`
- Testing:
  - Command: `python -m pytest -q tests/test_state_machine.py tests/test_dataset_etl_jobs.py tests/test_delta_utils.py tests/test_standardize_raw_inputs.py`
  - Result: `12 passed`
- Risks/Notes:
  - ARNs and resource names are templated placeholders for IaC substitution in Stage 06.
- Next:
  - Stage 06 IaC baseline.

## Next Stage Queue
1. Stage 06 - IaC baseline.
2. Stage 07 - Test suite expansion.
3. Stage 08 - CI/CD pipeline.
4. Stage 09 - Runbook and production validation flow.
