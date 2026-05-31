variable "project_name" {
  type = string
}

variable "stepfunctions_role_arn" {
  type = string
}

variable "state_machine_definition_path" {
  type = string
}

variable "detect_new_files_lambda_arn" {
  type = string
}

variable "catalog_update_lambda_arn" {
  type = string
}

variable "athena_validation_lambda_arn" {
  type = string
}

variable "archive_files_lambda_arn" {
  type = string
}

variable "failure_notifications_topic_arn" {
  type = string
}

variable "products_glue_job_name" {
  type = string
}

variable "orders_glue_job_name" {
  type = string
}

variable "order_items_glue_job_name" {
  type = string
}
