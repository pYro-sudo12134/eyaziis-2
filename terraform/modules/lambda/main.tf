resource "aws_lambda_function" "this" {
  for_each = var.functions

  function_name    = "${each.key}-${var.environment}"
  role             = var.lambda_role_arn
  handler          = each.value.handler
  runtime          = "python3.11"
  timeout          = each.value.timeout
  memory_size      = each.value.memory_size
  filename         = "${var.build_dir}/${each.key}.zip"
  source_code_hash = filebase64sha256("${var.build_dir}/${each.key}.zip")

  environment {
    variables = each.value.environment
  }
}

resource "aws_lambda_permission" "apigw" {
  for_each = toset(["ingest", "get_result"])

  statement_id  = "AllowAPIGateway-${each.key}"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this[each.key].function_name
  principal     = "apigateway.amazonaws.com"
}