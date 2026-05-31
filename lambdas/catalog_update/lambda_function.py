import os
import boto3


def handler(event, _context):
    glue = boto3.client("glue")
    database = os.environ["GLUE_DATABASE_NAME"]
    tables = event.get("tables", ["orders", "products", "order_items"])
    locations = event.get("locations", {})

    updated = []
    for table in tables:
        location = locations.get(table, f"s3://{os.environ['LAKEHOUSE_BUCKET']}/processed/{table}/")
        glue.update_table(
            DatabaseName=database,
            TableInput={
                "Name": table,
                "TableType": "EXTERNAL_TABLE",
                "StorageDescriptor": {
                    "Columns": [],
                    "Location": location,
                    "InputFormat": "org.apache.hadoop.mapred.SequenceFileInputFormat",
                    "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveSequenceFileOutputFormat",
                    "SerdeInfo": {"SerializationLibrary": "org.openx.data.jsonserde.JsonSerDe", "Parameters": {}},
                },
                "Parameters": {"classification": "delta"},
            },
        )
        updated.append(table)

    return {
        "statusCode": 200,
        "message": "Catalog update succeeded.",
        "updated_tables": updated,
    }
