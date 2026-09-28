variable "environment" {
  type = string
}

variable "lambda_role_arn" {
  type = string
}

variable "build_dir" {
  type = string
}

variable "functions" {
  type = map(object({
    handler     = string
    timeout     = number
    memory_size = number
    environment = map(string)
  }))
}