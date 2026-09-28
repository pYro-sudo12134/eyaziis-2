variable "environment" {
  type = string
}

variable "s3_bucket_arns" {
  type = list(string)
}

variable "sqs_queue_arns" {
  type = list(string)
}

variable "secrets_arns" {
  type = list(string)
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}