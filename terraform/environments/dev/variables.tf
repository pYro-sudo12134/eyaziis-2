variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "aws_access_key_id" {
  type      = string
  default   = "test"
  sensitive = true
}

variable "aws_secret_access_key" {
  type      = string
  default   = "test"
  sensitive = true
}

variable "aws_endpoint_url" {
  type        = string
  description = "LocalStack endpoint из хоста"
  default     = "http://localhost:4566"
}

variable "aws_internal_endpoint" {
  type        = string
  description = "LocalStack endpoint внутри Docker-сети"
  default     = "http://localstack:4566"
}

variable "aws_external_endpoint" {
  type        = string
  description = "LocalStack endpoint для клиента"
  default     = "http://localhost:4566"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "ollama_url" {
  type    = string
  default = "http://ollama1:11435"
}

variable "ollama_formalize_model" {
  type    = string
  default = "qwen2.5:0.5b"
}

variable "ollama_execute_model" {
  type    = string
  default = "qwen2.5:3b"
}

variable "ollama_embed_model" {
  type    = string
  default = "nomic-embed-text"
}

variable "qdrant_url" {
  type    = string
  default = "http://qdrant:6333"
}

variable "qdrant_collection" {
  type    = string
  default = "literature"
}

variable "qdrant_api_key" {
  type      = string
  default   = ""
  sensitive = true
}

variable "tts_service_url" {
  type    = string
  default = "http://tts-service:8000"
}

variable "transcribe_language" {
  type    = string
  default = "ru-RU"
}