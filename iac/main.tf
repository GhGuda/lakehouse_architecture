terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "s3" {
  source                        = "./modules/s3"
  lakehouse_bucket_name         = var.lakehouse_bucket_name
  products_script_path          = "${path.module}/../glue_jobs/products_etl.py"
  orders_script_path            = "${path.module}/../glue_jobs/orders_etl.py"
  order_items_script_path       = "${path.module}/../glue_jobs/order_items_etl.py"
  state_machine_definition_path = "${path.module}/../stepfunctions/state_machine.json"
}

module "iam" {
  source               = "./modules/iam"
  project_name         = var.project_name
  lakehouse_bucket_arn = module.s3.bucket_arn
}

module "glue" {
  source                 = "./modules/glue"
  project_name           = var.project_name
  glue_job_role_arn      = module.iam.glue_job_role_arn
  bucket_id              = module.s3.bucket_id
  products_script_key    = module.s3.products_script_key
  orders_script_key      = module.s3.orders_script_key
  order_items_script_key = module.s3.order_items_script_key
}

module "stepfunctions" {
  source                          = "./modules/stepfunctions"
  project_name                    = var.project_name
  stepfunctions_role_arn          = module.iam.stepfunctions_role_arn
  state_machine_definition_path   = "${path.module}/../stepfunctions/state_machine.json"
  detect_new_files_lambda_arn     = var.detect_new_files_lambda_arn
  catalog_update_lambda_arn       = var.catalog_update_lambda_arn
  athena_validation_lambda_arn    = var.athena_validation_lambda_arn
  archive_files_lambda_arn        = var.archive_files_lambda_arn
  failure_notifications_topic_arn = var.failure_notifications_topic_arn
  products_glue_job_name          = module.glue.products_job_name
  orders_glue_job_name            = module.glue.orders_job_name
  order_items_glue_job_name       = module.glue.order_items_job_name
}
