import os
import time
import boto3


def handler(event, _context):
    athena = boto3.client("athena")
    workgroup = os.environ.get("ATHENA_WORKGROUP", "primary")
    output = os.environ["ATHENA_OUTPUT_LOCATION"]
    query = event.get(
        "query",
        "SELECT COUNT(*) AS invalid_total_amounts FROM lakehouse_dwh.orders WHERE total_amount < 0",
    )

    start = athena.start_query_execution(
        QueryString=query,
        WorkGroup=workgroup,
        ResultConfiguration={"OutputLocation": output},
    )
    qid = start["QueryExecutionId"]

    state = "RUNNING"
    while state in {"QUEUED", "RUNNING"}:
        resp = athena.get_query_execution(QueryExecutionId=qid)
        state = resp["QueryExecution"]["Status"]["State"]
        if state in {"QUEUED", "RUNNING"}:
            time.sleep(1)

    if state != "SUCCEEDED":
        return {"statusCode": 500, "validation_passed": False, "query_execution_id": qid, "state": state}

    results = athena.get_query_results(QueryExecutionId=qid)
    rows = results["ResultSet"]["Rows"]
    invalid_count = int(rows[1]["Data"][0]["VarCharValue"]) if len(rows) > 1 else 0
    return {
        "statusCode": 200,
        "validation_passed": invalid_count == 0,
        "invalid_count": invalid_count,
        "query_execution_id": qid,
    }
