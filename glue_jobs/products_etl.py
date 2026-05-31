"""Products dataset ETL job."""

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


def run_products_etl(input_file: Path) -> dict[str, object]:
    """Process product records into curated and invalid sets with manifest metadata."""
    dataframe = pd.read_csv(input_file)
    validate_required_columns(list(dataframe.columns), ["product_id"])

    rules = [ValidationRule("product_id_required", lambda frame: frame["product_id"].notna())]
    valid_records, invalid_records = split_valid_invalid_records(dataframe, rules)
    curated = deduplicate_by_key(valid_records, key_columns=["product_id"], order_column="product_id")

    return {
        "curated_df": curated,
        "invalid_df": invalid_records,
        "manifest": build_processed_file_manifest("products", [input_file]),
    }
