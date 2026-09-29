resource "aws_lambda_function" "this" {
  for_each = var.functions

  function_name                  = "${each.key}-${var.environment}"
  role                           = var.lambda_role_arn
  handler                        = each.value.handler
  runtime                        = "python3.11"
  timeout                        = each.value.timeout
  memory_size                    = each.value.memory_size
  reserved_concurrent_executions = 10
  filename                       = "${var.build_dir}/${each.key}.zip"
  source_code_hash               = filebase64sha256("${var.build_dir}/${each.key}.zip")

  dead_letter_config {
    target_arn = var.lambda_dlq_arn
  }

  environment {
    variables = each.value.environment
  }

  timeouts {
    create = "5m"
    update = "5m"
  }
}

resource "aws_lambda_permission" "apigw" {
  for_each = toset(["ingest", "get_result"])

  statement_id  = "AllowAPIGateway-${each.key}"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this[each.key].function_name
  principal     = "apigateway.amazonaws.com"
}