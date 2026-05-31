from pathlib import Path

import pandas as pd
import pytest

from glue_jobs.utils.delta_utils import (
    DataValidationError,
    ValidationRule,
    build_processed_file_manifest,
    deduplicate_by_key,
    split_valid_invalid_records,
    validate_required_columns,
)


def test_validate_required_columns_raises_on_missing_columns() -> None:
    with pytest.raises(DataValidationError, match="Missing required column"):
        validate_required_columns(columns=["order_id", "user_id"], required_columns=["order_id", "date"])


def test_split_valid_invalid_records_applies_all_rules() -> None:
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "total_amount": [10.5, -4.0, 0.0],
            "user_id": [99, None, 42],
        }
    )
    rules = [
        ValidationRule("non_negative_total", lambda frame: frame["total_amount"] >= 0),
        ValidationRule("user_required", lambda frame: frame["user_id"].notna()),
    ]

    valid, invalid = split_valid_invalid_records(df, rules)

    assert len(valid) == 2
    assert len(invalid) == 1
    assert invalid.iloc[0]["order_id"] == 2


def test_deduplicate_by_key_keeps_latest_record() -> None:
    df = pd.DataFrame(
        {
            "order_id": [1, 1, 2],
            "ingestion_timestamp": [1, 2, 1],
            "total_amount": [10.0, 12.0, 7.5],
        }
    )

    result = deduplicate_by_key(df, key_columns=["order_id"], order_column="ingestion_timestamp")
    assert len(result) == 2
    latest_for_one = result[result["order_id"] == 1].iloc[0]
    assert latest_for_one["total_amount"] == 12.0


def test_build_processed_file_manifest_shapes_expected_fields() -> None:
    manifest = build_processed_file_manifest(
        dataset="orders",
        source_files=[Path("raw/orders/orders_2025-04-01.csv")],
    )

    assert len(manifest) == 1
    assert manifest[0]["dataset"] == "orders"
    assert manifest[0]["source_file"].endswith("orders_2025-04-01.csv")
    assert "processed_at" in manifest[0]
