variable "parameters" {
  type = map(object({
    type  = string
    value = string
  }))
}