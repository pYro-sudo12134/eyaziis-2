variable "aws_region" {
  default = "us-east-1"
}

variable "aws_access_key_id" {
  default   = "test"
  sensitive = true
}

variable "aws_secret_access_key" {
  default   = "test"
  sensitive = true
}

variable "aws_endpoint_url" {
  description = "LocalStack endpoint из хоста"
  default     = "http://localhost:4566"
}

variable "aws_internal_endpoint" {
  description = "LocalStack endpoint внутри Docker-сети"
  default     = "http://localstack:4566"
}

variable "aws_external_endpoint" {
  description = "LocalStack endpoint для клиента"
  default     = "http://localhost:4566"
}

variable "environment" {
  default = "dev"
}

variable "ollama_url" {
  default = "http://ollama:11434"
}

variable "ollama_formalize_model" {
  default = "qwen2.5:0.5b"
}

variable "ollama_execute_model" {
  default = "qwen2.5:3b"
}

variable "ollama_embed_model" {
  default = "nomic-embed-text"
}

variable "qdrant_url" {
  default = "http://qdrant:6333"
}

variable "qdrant_collection" {
  default = "literature"
}

variable "qdrant_api_key" {
  default   = ""
  sensitive = true
}

variable "tts_service_url" {
  default = "http://tts-service:8000"
}

variable "transcribe_language" {
  default = "ru-RU"
}