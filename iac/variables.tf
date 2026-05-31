variable "project_name" {
  type        = string
  description = "Project prefix for named resources."
  default     = "lakehouse-architecture"
}

variable "aws_region" {
  type        = string
  description = "AWS region for deployment."
  default     = "us-east-1"
}

variable "lakehouse_bucket_name" {
  type        = string
  description = "S3 bucket used for lakehouse data and deployment artifacts."
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
