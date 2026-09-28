variable "environment" {
  type = string
}

variable "sfn_role_arn" {
  type = string
}

variable "lambda_function_arns" {
  type = map(string)
}

variable "sqs_tts_url" {
  type = string
}