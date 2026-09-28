resource "aws_api_gateway_rest_api" "this" {
  name        = "api-${var.environment}"
  description = "Speech synthesis API"
}

# === /ask ===
resource "aws_api_gateway_resource" "ask" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_rest_api.this.root_resource_id
  path_part   = "ask"
}

resource "aws_api_gateway_method" "ask_post" {
  rest_api_id   = aws_api_gateway_rest_api.this.id
  resource_id   = aws_api_gateway_resource.ask.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "ask_post" {
  rest_api_id             = aws_api_gateway_rest_api.this.id
  resource_id             = aws_api_gateway_resource.ask.id
  http_method             = aws_api_gateway_method.ask_post.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${var.lambda_function_arns["ingest"]}/invocations"
}

# === /ask-audio ===
resource "aws_api_gateway_resource" "ask_audio" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_rest_api.this.root_resource_id
  path_part   = "ask-audio"
}

resource "aws_api_gateway_method" "ask_audio_post" {
  rest_api_id   = aws_api_gateway_rest_api.this.id
  resource_id   = aws_api_gateway_resource.ask_audio.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "ask_audio_post" {
  rest_api_id             = aws_api_gateway_rest_api.this.id
  resource_id             = aws_api_gateway_resource.ask_audio.id
  http_method             = aws_api_gateway_method.ask_audio_post.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${var.lambda_function_arns["ingest"]}/invocations"
}

# === /result/{request_id} ===
resource "aws_api_gateway_resource" "result" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_rest_api.this.root_resource_id
  path_part   = "result"
}

resource "aws_api_gateway_resource" "result_id" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.result.id
  path_part   = "{request_id}"
}

resource "aws_api_gateway_method" "result_get" {
  rest_api_id   = aws_api_gateway_rest_api.this.id
  resource_id   = aws_api_gateway_resource.result_id.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.path.request_id" = true
  }
}

resource "aws_api_gateway_integration" "result_get" {
  rest_api_id             = aws_api_gateway_rest_api.this.id
  resource_id             = aws_api_gateway_resource.result_id.id
  http_method             = aws_api_gateway_method.result_get.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${var.lambda_function_arns["get_result"]}/invocations"
}

# === Deployment ===
resource "aws_api_gateway_deployment" "this" {
  rest_api_id = aws_api_gateway_rest_api.this.id

  depends_on = [
    aws_api_gateway_integration.ask_post,
    aws_api_gateway_integration.ask_audio_post,
    aws_api_gateway_integration.result_get,
  ]

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "this" {
  deployment_id = aws_api_gateway_deployment.this.id
  rest_api_id   = aws_api_gateway_rest_api.this.id
  stage_name    = var.environment
}