"""Shared ETL utilities for lakehouse Glue jobs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

import pandas as pd


class DataValidationError(Exception):
    """Raised when required dataset structure is not satisfied."""


@dataclass(frozen=True)
class ValidationRule:
    """Represents a named boolean rule applied to each record."""

    name: str
    predicate: Callable[[pd.DataFrame], pd.Series]


def validate_required_columns(columns: list[str], required_columns: list[str]) -> None:
    """Validate that all required columns exist."""
    missing = sorted(set(required_columns) - set(columns))
    if missing:
        raise DataValidationError(f"Missing required column(s): {', '.join(missing)}")


def split_valid_invalid_records(
    dataframe: pd.DataFrame, rules: list[ValidationRule]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split records into valid and invalid dataframes based on all rules."""
    if dataframe.empty:
        return dataframe.copy(), dataframe.copy()

    mask = pd.Series(True, index=dataframe.index)
    for rule in rules:
        rule_mask = rule.predicate(dataframe).fillna(False)
        if len(rule_mask) != len(dataframe):
            raise DataValidationError(f"Validation rule returned invalid mask length: {rule.name}")
        mask &= rule_mask

    valid_records = dataframe[mask].copy()
    invalid_records = dataframe[~mask].copy()
    return valid_records, invalid_records


def deduplicate_by_key(
    dataframe: pd.DataFrame, key_columns: list[str], order_column: str
) -> pd.DataFrame:
    """Deduplicate records by key, keeping the latest row by order column."""
    validate_required_columns(list(dataframe.columns), key_columns + [order_column])
    ordered = dataframe.sort_values(order_column).copy()
    deduplicated = ordered.drop_duplicates(subset=key_columns, keep="last")
    return deduplicated.reset_index(drop=True)


def build_processed_file_manifest(dataset: str, source_files: list[Path]) -> list[dict[str, str]]:
    """Build metadata entries used by orchestration for archival handoff."""
    processed_at = datetime.now(UTC).isoformat()
    manifest: list[dict[str, str]] = []
    for file_path in source_files:
        manifest.append(
            {
                "dataset": dataset,
                "source_file": str(file_path),
                "processed_at": processed_at,
            }
        )
    return manifest
