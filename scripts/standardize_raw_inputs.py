from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Final

import pandas as pd

LOGGER: Final[logging.Logger] = logging.getLogger(__name__)


class StandardizationError(Exception):
    """Raised when source standardization fails due to invalid inputs or IO issues."""


def sanitize_sheet_name(sheet_name: str) -> str:
    """Return a filesystem-safe sheet label while preserving date-like names."""
    normalized = sheet_name.strip()
    if not normalized:
        raise StandardizationError("Encountered empty sheet name in workbook.")

    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", normalized)
    safe_name = safe_name.strip("._")
    if not safe_name:
        raise StandardizationError(f"Sheet name '{sheet_name}' is not valid for file output.")

    return safe_name


def validate_source_paths(data_dir: Path) -> None:
    """Validate that source directory exists and contains ingestible files."""
    if not data_dir.exists():
        raise StandardizationError(f"Source data directory does not exist: {data_dir}")
    candidates = list(data_dir.glob("*.xlsx")) + list(data_dir.glob("*.csv"))
    if not candidates:
        raise StandardizationError(f"No .xlsx or .csv files found in source directory: {data_dir}")


def infer_dataset_name(file_path: Path) -> str:
    """Infer dataset key from filename prefix before date suffixes."""
    stem = file_path.stem.lower()
    stem = re.sub(r"_apr_\d{4}$", "", stem)
    stem = re.sub(r"_\d{4}[-_]\d{2}[-_]\d{2}$", "", stem)
    return stem


def standardize_excel_workbook(input_path: Path, output_dir: Path, prefix: str) -> list[Path]:
    """Convert each sheet in an Excel workbook into one CSV file."""
    if not input_path.exists():
        raise StandardizationError(f"Workbook not found: {input_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        workbook = pd.ExcelFile(input_path)
    except Exception as exc:  # pragma: no cover
        raise StandardizationError(f"Unable to read workbook: {input_path}") from exc

    created_files: list[Path] = []

    for sheet_name in workbook.sheet_names:
        safe_sheet_name = sanitize_sheet_name(sheet_name)
        try:
            dataframe = workbook.parse(sheet_name=sheet_name)
        except Exception as exc:  # pragma: no cover
            raise StandardizationError(
                f"Unable to parse sheet '{sheet_name}' from workbook: {input_path}"
            ) from exc

        output_file = output_dir / f"{prefix}_{safe_sheet_name}.csv"
        try:
            dataframe.to_csv(output_file, index=False)
        except Exception as exc:  # pragma: no cover
            raise StandardizationError(f"Failed to write CSV output: {output_file}") from exc
        created_files.append(output_file)
        LOGGER.info("Wrote standardized sheet CSV: %s", output_file)

    return created_files


def copy_csv(input_path: Path, output_path: Path) -> Path:
    """Copy a CSV file by reading and writing through pandas for consistent formatting."""
    if not input_path.exists():
        raise StandardizationError(f"CSV input not found: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        dataframe = pd.read_csv(input_path)
        dataframe.to_csv(output_path, index=False)
    except Exception as exc:  # pragma: no cover
        raise StandardizationError(f"Failed to copy CSV from {input_path} to {output_path}") from exc

    LOGGER.info("Copied standardized CSV: %s", output_path)
    return output_path


def standardize_dataset(data_dir: Path, output_root: Path) -> dict[str, list[str]]:
    """Standardize all expected lakehouse inputs into deterministic CSV outputs."""
    validate_source_paths(data_dir)
    outputs: dict[str, list[str]] = {}
    for file_path in sorted(data_dir.iterdir()):
        if file_path.suffix.lower() not in {".xlsx", ".csv"}:
            continue

        dataset = infer_dataset_name(file_path)
        if file_path.suffix.lower() == ".xlsx":
            result_files = standardize_excel_workbook(
                input_path=file_path,
                output_dir=output_root / dataset,
                prefix=dataset,
            )
            outputs[dataset] = [str(path) for path in result_files]
        else:
            result_file = copy_csv(
                input_path=file_path,
                output_path=output_root / dataset / f"{dataset}.csv",
            )
            outputs[dataset] = [str(result_file)]

    return outputs
