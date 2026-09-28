resource "aws_dynamodb_table" "requests" {
  name         = "requests-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "request_id"

  attribute {
    name = "request_id"
    type = "S"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }

  tags = {
    Environment = var.environment
    Project     = "speech-pipeline"
  }
}