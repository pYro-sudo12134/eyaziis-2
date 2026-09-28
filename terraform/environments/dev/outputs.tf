output "api_gateway_url" {
  value = module.apigateway.api_url
}

output "state_machine_arn" {
  value = module.stepfunctions.state_machine_arn
}

output "s3_buckets" {
  value = module.s3.bucket_names
}

output "sqs_queues" {
  value = module.sqs.queue_urls
}

output "lambda_functions" {
  value = module.lambda.function_arns
}