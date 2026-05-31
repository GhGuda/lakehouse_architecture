output "glue_job_role_arn" {
  value = aws_iam_role.glue_job_role.arn
}

output "stepfunctions_role_arn" {
  value = aws_iam_role.stepfunctions_role.arn
}
