import os
from unittest.mock import MagicMock, patch

from lambdas.archive_files.lambda_function import handler as archive_handler
from lambdas.athena_validation.lambda_function import handler as athena_handler
from lambdas.catalog_update.lambda_function import handler as catalog_handler
from lambdas.detect_new_files.lambda_function import handler as detect_handler


@patch("lambdas.detect_new_files.lambda_function.boto3.client")
def test_detect_new_files(mock_client):
    s3 = MagicMock()
    s3.list_objects_v2.return_value = {"KeyCount": 1}
    mock_client.return_value = s3
    os.environ["LAKEHOUSE_BUCKET"] = "bucket"
    out = detect_handler({}, None)
    assert out["has_new_files"] is True


@patch("lambdas.catalog_update.lambda_function.boto3.client")
def test_catalog_update(mock_client):
    glue = MagicMock()
    mock_client.return_value = glue
    os.environ["GLUE_DATABASE_NAME"] = "lakehouse_dwh"
    os.environ["LAKEHOUSE_BUCKET"] = "bucket"
    out = catalog_handler({}, None)
    assert out["statusCode"] == 200
    assert "orders" in out["updated_tables"]


@patch("lambdas.athena_validation.lambda_function.time.sleep", return_value=None)
@patch("lambdas.athena_validation.lambda_function.boto3.client")
def test_athena_validation(mock_client, _sleep):
    athena = MagicMock()
    athena.start_query_execution.return_value = {"QueryExecutionId": "q1"}
    athena.get_query_execution.return_value = {"QueryExecution": {"Status": {"State": "SUCCEEDED"}}}
    athena.get_query_results.return_value = {
        "ResultSet": {"Rows": [{"Data": [{"VarCharValue": "invalid_total_amounts"}]}, {"Data": [{"VarCharValue": "0"}]}]}
    }
    mock_client.return_value = athena
    os.environ["ATHENA_OUTPUT_LOCATION"] = "s3://bucket/athena-results/"
    out = athena_handler({}, None)
    assert out["validation_passed"] is True


@patch("lambdas.archive_files.lambda_function.boto3.client")
def test_archive_files(mock_client):
    s3 = MagicMock()
    mock_client.return_value = s3
    os.environ["LAKEHOUSE_BUCKET"] = "bucket"
    out = archive_handler({"files": ["raw/orders/file1.csv"]}, None)
    assert out["statusCode"] == 200
    assert out["moved_files"][0]["to"].startswith("archived/")
