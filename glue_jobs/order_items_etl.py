"""Order items dataset ETL job."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from glue_jobs.utils.delta_utils import (
    ValidationRule,
    build_processed_file_manifest,
    deduplicate_by_key,
    split_valid_invalid_records,
    validate_required_columns,
)


def run_order_items_etl(
    input_files: list[Path], valid_product_ids: set[int], run_id: str
) -> dict[str, object]:
    """Process order item records and enforce product referential validity."""
    ingestion_timestamp = datetime.now(UTC).isoformat()
    dataframes: list[pd.DataFrame] = []
    for path in input_files:
        frame = pd.read_csv(path)
        frame["source_file"] = str(path)
        dataframes.append(frame)
    dataframe = pd.concat(dataframes, ignore_index=True) if dataframes else pd.DataFrame()

    validate_required_columns(
        list(dataframe.columns),
        ["id", "order_id", "product_id", "order_timestamp", "date"],
    )

    dataframe["ingestion_timestamp"] = ingestion_timestamp
    dataframe["run_id"] = run_id
    dataframe["order_timestamp"] = pd.to_datetime(dataframe["order_timestamp"], errors="coerce")
    # Preserve deterministic deduplication ordering for duplicate item ids.
    dataframe["ingestion_order"] = range(len(dataframe))

    rules = [
        ValidationRule("id_required", lambda frame: frame["id"].notna()),
        ValidationRule("order_id_required", lambda frame: frame["order_id"].notna()),
        ValidationRule("product_id_required", lambda frame: frame["product_id"].notna()),
        ValidationRule("timestamp_valid", lambda frame: frame["order_timestamp"].notna()),
        ValidationRule("product_exists", lambda frame: frame["product_id"].isin(valid_product_ids)),
    ]
    valid_records, invalid_records = split_valid_invalid_records(dataframe, rules)
    curated = deduplicate_by_key(valid_records, key_columns=["id"], order_column="ingestion_order")

    return {
        "curated_df": curated.drop(columns=["ingestion_order"]),
        "invalid_df": invalid_records.drop(columns=["ingestion_order"]),
        "manifest": build_processed_file_manifest("order_items", input_files),
    }
