import os
import boto3


def handler(event, _context):
    s3 = boto3.client("s3")
    bucket = event.get("bucket") or os.environ["LAKEHOUSE_BUCKET"]
    files = event.get("files", [])
    moved = []
    for key in files:
        if not key.startswith("raw/"):
            continue
        target_key = key.replace("raw/", "archived/", 1)
        s3.copy_object(Bucket=bucket, CopySource={"Bucket": bucket, "Key": key}, Key=target_key)
        s3.delete_object(Bucket=bucket, Key=key)
        moved.append({"from": key, "to": target_key})

    return {
        "statusCode": 200,
        "message": "Archive operation succeeded.",
        "moved_files": moved,
        "execution_id": event.get("execution_id", "unknown"),
    }
