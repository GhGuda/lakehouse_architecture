resource "aws_s3_bucket" "lakehouse" {
  bucket = var.lakehouse_bucket_name
}

resource "aws_s3_object" "glue_script_products" {
  bucket = aws_s3_bucket.lakehouse.id
  key    = "artifacts/glue_jobs/products_etl.py"
  source = var.products_script_path
  etag   = filemd5(var.products_script_path)
}

resource "aws_s3_object" "glue_script_orders" {
  bucket = aws_s3_bucket.lakehouse.id
  key    = "artifacts/glue_jobs/orders_etl.py"
  source = var.orders_script_path
  etag   = filemd5(var.orders_script_path)
}

resource "aws_s3_object" "glue_script_order_items" {
  bucket = aws_s3_bucket.lakehouse.id
  key    = "artifacts/glue_jobs/order_items_etl.py"
  source = var.order_items_script_path
  etag   = filemd5(var.order_items_script_path)
}

resource "aws_s3_object" "stepfunction_definition" {
  bucket = aws_s3_bucket.lakehouse.id
  key    = "artifacts/stepfunctions/state_machine.json"
  source = var.state_machine_definition_path
  etag   = filemd5(var.state_machine_definition_path)
}
