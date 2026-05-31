import os
import boto3


def handler(event, _context):
    bucket = event.get("bucket") or os.environ["LAKEHOUSE_BUCKET"]
    prefixes = event.get("prefixes", ["raw/orders/", "raw/order_items/", "raw/products/"])
    s3 = boto3.client("s3")
    has_new = False
    for prefix in prefixes:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=1)
        if response.get("KeyCount", 0) > 0:
            has_new = True
            break
    return {"statusCode": 200, "has_new_files": has_new}
