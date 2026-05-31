from pathlib import Path

import pandas as pd
import pytest

from glue_jobs.order_items_etl import run_order_items_etl
from glue_jobs.orders_etl import run_orders_etl
from glue_jobs.utils.delta_utils import DataValidationError, deduplicate_by_key


def _write_csv(path: Path, dataframe: pd.DataFrame) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(path, index=False)
    return path


def test_orders_etl_raises_when_required_columns_missing(tmp_path: Path) -> None:
    file_path = _write_csv(
        tmp_path / "orders.csv",
        pd.DataFrame({"order_id": [1], "user_id": [2]}),
    )
    with pytest.raises(DataValidationError, match="Missing required column"):
        run_orders_etl([file_path], run_id="run-missing-cols")


def test_order_items_etl_marks_unknown_products_invalid(tmp_path: Path) -> None:
    file_path = _write_csv(
        tmp_path / "order_items.csv",
        pd.DataFrame(
            {
                "id": [1, 2],
                "order_id": [100, 101],
                "product_id": [1, 999],
                "order_timestamp": ["2025-04-01T00:00:00", "2025-04-01T00:10:00"],
                "date": ["2025-04-01", "2025-04-01"],
            }
        ),
    )
    result = run_order_items_etl([file_path], valid_product_ids={1}, run_id="run-ref-check")
    assert len(result["curated_df"]) == 1
    assert len(result["invalid_df"]) == 1


def test_deduplicate_by_key_raises_for_missing_order_column() -> None:
    dataframe = pd.DataFrame({"id": [1, 1], "value": [10, 20]})
    with pytest.raises(DataValidationError, match="Missing required column"):
        deduplicate_by_key(dataframe, key_columns=["id"], order_column="ingestion_order")
