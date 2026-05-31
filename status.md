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
- Status: Completed
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
- Status: Completed
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

### Stage 06 - IaC Baseline
- Date: 2026-05-31
- Branch: `feat/stage-06-iac-baseline`
- Status: Completed
- Scope:
  - Add Terraform baseline for S3, IAM, Glue jobs, and Step Functions integration.
- Delivered:
  - Refactored IaC into modules for maintainability:
    - `iac/modules/s3`
    - `iac/modules/iam`
    - `iac/modules/glue`
    - `iac/modules/stepfunctions`
  - Rewired root composition in `iac/main.tf`.
  - Added root `iac/variables.tf` and `iac/outputs.tf`.
- Testing:
  - Command: `terraform fmt iac`
  - Result: formatting applied successfully.
  - Command: `python -m pytest -q tests/test_state_machine.py tests/test_dataset_etl_jobs.py tests/test_delta_utils.py tests/test_standardize_raw_inputs.py`
  - Result: `12 passed`
- Risks/Notes:
  - `terraform init/validate/plan` not run yet because deployment-time variables and AWS credentials are environment-dependent.
- Next:
  - Stage 07 test suite expansion.

### Stage 07 - Test Suite Expansion
- Date: 2026-05-31
- Branch: `feat/stage-07-test-suite-expansion`
- Status: Completed
- Scope:
  - Expand tests to cover ETL edge cases and IaC structural integrity.
- Delivered:
  - Added `tests/test_etl_edge_cases.py` for:
    - required-column failure path
    - referential validation behavior
    - deduplication missing-order-column error path
  - Added `tests/test_iac_structure.py` to validate modular Terraform layout.
- Testing:
  - Command: `python -m pytest -q`
  - Result: `17 passed`
- Risks/Notes:
  - Tests remain local/static; Terraform runtime validation still depends on environment credentials and deployment variables.
- Next:
  - Stage 08 CI/CD pipeline.

### Stage 08 - CI/CD Pipeline
- Date: 2026-05-31
- Branch: `feat/stage-08-cicd-pipeline`
- Status: Completed (local)
- Scope:
  - Add GitHub Actions workflow for automated test, Terraform checks, and main-branch deploy.
- Delivered:
  - Added `.github/workflows/ci-cd.yml` with:
    - `test` job (`pytest`)
    - `terraform-check` job (`fmt`, `init`, `validate`)
    - `deploy` job gated to `push` on `main` with OIDC AWS auth and Terraform `plan/apply`
  - Updated `README.md` with required GitHub Action variables and secret.
- Testing:
  - Command: `python -m pytest -q`
  - Result: `17 passed`
- Risks/Notes:
  - Deployment job requires repository-level AWS/OIDC configuration and deployment variable values.
- Next:
  - Stage 09 runbook and production validation flow.

### Stage 09 - Runbook and Production Validation Flow
- Date: 2026-05-31
- Branch: `feat/stage-09-runbook-validation`
- Status: Completed (local)
- Scope:
  - Add an operational runbook that enables execution, validation, recovery, and handoff in production.
- Delivered:
  - Added `docs/runbook.md` covering:
    - daily operations
    - pre/post deployment checks
    - Athena validation queries
    - quarantine and reprocessing procedures
    - failure recovery and backfill procedures
    - observability and on-call handoff template
- Testing:
  - Documentation deliverable verified for completeness and alignment with implemented architecture.
- Risks/Notes:
  - Final production readiness still depends on actual AWS environment provisioning and secret/variable setup.
- Next:
  - Project implementation stages complete; proceed with PR consolidation/review and deployment rollout.

### Stage 10 - Production Readiness Gap Closure
- Date: 2026-05-31
- Branch: `feat/stage-10-production-readiness`
- Status: Completed (local)
- Scope:
  - Close remaining practical gaps for first AWS dry run.
- Delivered:
  - Implemented Lambda handlers with `boto3` production logic:
    - `lambdas/detect_new_files/lambda_function.py`
    - `lambdas/catalog_update/lambda_function.py`
    - `lambdas/athena_validation/lambda_function.py`
    - `lambdas/archive_files/lambda_function.py`
  - Added unit tests: `tests/test_lambda_handlers.py`
  - Kept ETL modules as pure callable functions (no CLI entrypoint in core job modules).
  - Added `docs/production_readiness.md` with deployment and first-run checklist.
- Testing:
  - Python tests executed successfully after ETL entrypoint additions.
- Risks/Notes:
  - Glue catalog schema descriptors and Athena query set should be hardened further per final table definitions and partition strategy.
