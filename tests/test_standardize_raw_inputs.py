from pathlib import Path

import pytest

from scripts.standardize_raw_inputs import (
    StandardizationError,
    sanitize_sheet_name,
    standardize_dataset,
)


def test_standardize_dataset_creates_expected_files(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    data_dir = repo_root / "Data"

    outputs = standardize_dataset(data_dir=data_dir, output_root=tmp_path)

    assert len(outputs["orders"]) == 15
    assert len(outputs["order_items"]) == 15
    assert len(outputs["products"]) == 1

    for output_list in outputs.values():
        for output_file in output_list:
            assert Path(output_file).exists()


def test_orders_output_contains_expected_header(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    data_dir = repo_root / "Data"

    standardize_dataset(data_dir=data_dir, output_root=tmp_path)
    orders_file = tmp_path / "orders" / "orders_2025-04-01.csv"

    header = orders_file.read_text(encoding="utf-8").splitlines()[0]
    assert header == "order_num,order_id,user_id,order_timestamp,total_amount,date"


def test_standardize_dataset_raises_for_missing_required_files(tmp_path: Path) -> None:
    with pytest.raises(StandardizationError, match="No .xlsx or .csv files found"):
        standardize_dataset(data_dir=tmp_path, output_root=tmp_path / "out")


def test_sanitize_sheet_name_rejects_empty_input() -> None:
    with pytest.raises(StandardizationError, match="empty sheet name"):
        sanitize_sheet_name("   ")
