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
- Status: Completed (local)
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

## Next Stage Queue
1. Stage 03 - Shared ETL utilities.
2. Stage 04 - Dataset ETL jobs.
3. Stage 05 - Step Functions orchestration.
4. Stage 06 - IaC baseline.
5. Stage 07 - Test suite expansion.
6. Stage 08 - CI/CD pipeline.
7. Stage 09 - Runbook and production validation flow.
