output "api_url" {
  value = "http://${aws_api_gateway_rest_api.this.id}.execute-api.localhost.localstack.cloud:4566/${var.environment}"
}

output "api_id" {
  value = aws_api_gateway_rest_api.this.id
}