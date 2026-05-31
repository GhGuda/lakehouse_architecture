"""Orders dataset ETL job."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from glue_jobs.utils.delta_utils import (
    ValidationRule,
    build_processed_file_manifest,
    deduplicate_by_key,
    split_valid_invalid_records,
    validate_required_columns,
)


def run_orders_etl(input_files: list[Path]) -> dict[str, object]:
    """Process order records with validation and latest-by-key deduplication."""
    dataframes = [pd.read_csv(path) for path in input_files]
    dataframe = pd.concat(dataframes, ignore_index=True) if dataframes else pd.DataFrame()

    validate_required_columns(
        list(dataframe.columns),
        ["order_id", "user_id", "order_timestamp", "total_amount", "date"],
    )

    dataframe["order_timestamp"] = pd.to_datetime(dataframe["order_timestamp"], errors="coerce")
    # Keep stable ingestion precedence so duplicate keys retain the most recent row in this run.
    dataframe["ingestion_order"] = range(len(dataframe))

    rules = [
        ValidationRule("order_id_required", lambda frame: frame["order_id"].notna()),
        ValidationRule("user_id_required", lambda frame: frame["user_id"].notna()),
        ValidationRule("timestamp_valid", lambda frame: frame["order_timestamp"].notna()),
        ValidationRule("non_negative_total", lambda frame: frame["total_amount"].fillna(-1) >= 0),
    ]
    valid_records, invalid_records = split_valid_invalid_records(dataframe, rules)
    curated = deduplicate_by_key(valid_records, key_columns=["order_id"], order_column="ingestion_order")

    return {
        "curated_df": curated.drop(columns=["ingestion_order"]),
        "invalid_df": invalid_records.drop(columns=["ingestion_order"]),
        "manifest": build_processed_file_manifest("orders", input_files),
    }
