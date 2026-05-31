output "lakehouse_bucket_id" {
  value = module.s3.bucket_id
}

output "state_machine_arn" {
  value = module.stepfunctions.state_machine_arn
}
