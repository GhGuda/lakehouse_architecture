resource "aws_glue_job" "products" {
  name     = "${var.project_name}-products-etl"
  role_arn = var.glue_job_role_arn
  command {
    script_location = "s3://${var.bucket_id}/${var.products_script_key}"
    python_version  = "3"
  }
  glue_version      = "4.0"
  number_of_workers = 2
  worker_type       = "G.1X"
}

resource "aws_glue_job" "orders" {
  name     = "${var.project_name}-orders-etl"
  role_arn = var.glue_job_role_arn
  command {
    script_location = "s3://${var.bucket_id}/${var.orders_script_key}"
    python_version  = "3"
  }
  glue_version      = "4.0"
  number_of_workers = 2
  worker_type       = "G.1X"
}

resource "aws_glue_job" "order_items" {
  name     = "${var.project_name}-order-items-etl"
  role_arn = var.glue_job_role_arn
  command {
    script_location = "s3://${var.bucket_id}/${var.order_items_script_key}"
    python_version  = "3"
  }
  glue_version      = "4.0"
  number_of_workers = 2
  worker_type       = "G.1X"
}
