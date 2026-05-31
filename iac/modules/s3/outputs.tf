output "bucket_id" {
  value = aws_s3_bucket.lakehouse.id
}

output "bucket_arn" {
  value = aws_s3_bucket.lakehouse.arn
}

output "products_script_key" {
  value = aws_s3_object.glue_script_products.key
}

output "orders_script_key" {
  value = aws_s3_object.glue_script_orders.key
}

output "order_items_script_key" {
  value = aws_s3_object.glue_script_order_items.key
}
