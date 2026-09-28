variable "environment" {
  type = string
}

variable "queues" {
  type = map(object({
    visibility_timeout = number
    max_receive_count  = number
  }))
}