output "products_job_name" {
  value = aws_glue_job.products.name
}

output "orders_job_name" {
  value = aws_glue_job.orders.name
}

output "order_items_job_name" {
  value = aws_glue_job.order_items.name
}
