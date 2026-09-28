variable "environment" {
  type = string
}

variable "secrets" {
  type = map(object({
    description = string
    value       = string
  }))
}