output "parameter_names" {
  value = { for k, v in aws_ssm_parameter.this : k => v.name }
}