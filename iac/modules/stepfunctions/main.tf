locals {
  state_machine_definition = templatefile(var.state_machine_definition_path, {
    detect_new_files_lambda_arn     = var.detect_new_files_lambda_arn
    catalog_update_lambda_arn       = var.catalog_update_lambda_arn
    athena_validation_lambda_arn    = var.athena_validation_lambda_arn
    archive_files_lambda_arn        = var.archive_files_lambda_arn
    failure_notifications_topic_arn = var.failure_notifications_topic_arn
    products_glue_job_name          = var.products_glue_job_name
    orders_glue_job_name            = var.orders_glue_job_name
    order_items_glue_job_name       = var.order_items_glue_job_name
  })
}

resource "aws_sfn_state_machine" "lakehouse_orchestrator" {
  name       = "${var.project_name}-orchestrator"
  role_arn   = var.stepfunctions_role_arn
  definition = local.state_machine_definition
}
