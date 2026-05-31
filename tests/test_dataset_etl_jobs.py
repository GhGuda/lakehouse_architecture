from pathlib import Path

import pandas as pd

from glue_jobs.order_items_etl import run_order_items_etl
from glue_jobs.orders_etl import run_orders_etl
from glue_jobs.products_etl import run_products_etl


def _write_csv(path: Path, dataframe: pd.DataFrame) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(path, index=False)
    return path


def test_run_products_etl_deduplicates_and_splits_invalid(tmp_path: Path) -> None:
    file_path = _write_csv(
        tmp_path / "products.csv",
        pd.DataFrame(
            {
                "product_id": [1, 1, None, 2],
                "department": ["A", "B", "C", "D"],
            }
        ),
    )
    result = run_products_etl(file_path)
    assert len(result["curated_df"]) == 2
    assert len(result["invalid_df"]) == 1


def test_run_orders_etl_filters_invalid_and_deduplicates(tmp_path: Path) -> None:
    file_path = _write_csv(
        tmp_path / "orders_2025-04-01.csv",
        pd.DataFrame(
            {
                "order_id": [10, 10, 11],
                "user_id": [5, 6, 2],
                "order_timestamp": ["2025-04-01T10:00:00", "2025-04-01T12:00:00", "bad-date"],
                "total_amount": [12.3, 15.0, 1.0],
                "date": ["2025-04-01", "2025-04-01", "2025-04-01"],
            }
        ),
    )
    result = run_orders_etl([file_path])
    assert len(result["curated_df"]) == 1
    assert len(result["invalid_df"]) == 1
    assert result["curated_df"].iloc[0]["user_id"] == 6


def test_run_order_items_etl_checks_product_reference(tmp_path: Path) -> None:
    file_path = _write_csv(
        tmp_path / "order_items_2025-04-01.csv",
        pd.DataFrame(
            {
                "id": [1, 2],
                "order_id": [100, 101],
                "product_id": [200, 999],
                "order_timestamp": ["2025-04-01T08:00:00", "2025-04-01T09:00:00"],
                "date": ["2025-04-01", "2025-04-01"],
            }
        ),
    )
    result = run_order_items_etl([file_path], valid_product_ids={200})
    assert len(result["curated_df"]) == 1
    assert len(result["invalid_df"]) == 1
    assert result["curated_df"].iloc[0]["product_id"] == 200
