terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region                      = var.aws_region
  access_key                  = var.aws_access_key_id
  secret_key                  = var.aws_secret_access_key
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    s3             = var.aws_endpoint_url
    sqs            = var.aws_endpoint_url
    lambda         = var.aws_endpoint_url
    stepfunctions  = var.aws_endpoint_url
    iam            = var.aws_endpoint_url
    apigateway     = var.aws_endpoint_url
    transcribe     = var.aws_endpoint_url
    secretsmanager = var.aws_endpoint_url
    ssm            = var.aws_endpoint_url
  }

  s3_use_path_style = true
}

# === SSM ===
module "ssm" {
  source = "../../modules/ssm"

  parameters = {
    "/pipeline/${var.environment}/state_machine_arn" = {
      type  = "String"
      value = module.stepfunctions.state_machine_arn
    }
  }
}

# === S3 ===
module "s3" {
  source = "../../modules/s3"

  environment = var.environment
  buckets = {
    audio_input  = "audio-input-${var.environment}"
    audio_output = "audio-output-${var.environment}"
    transcripts  = "transcripts-${var.environment}"
    rag_docs     = "rag-documents-${var.environment}"
  }
}

# === SQS ===
module "sqs" {
  source = "../../modules/sqs"

  environment = var.environment
  queues = {
    input  = { visibility_timeout = 60, max_receive_count = 3 }
    tts    = { visibility_timeout = 120, max_receive_count = 3 }
    output = { visibility_timeout = 60, max_receive_count = 3 }
  }
}

# === IAM ===
module "iam" {
  source = "../../modules/iam"

  aws_region        = var.aws_region
  environment       = var.environment
  s3_bucket_arns    = values(module.s3.bucket_arns)
  sqs_queue_arns    = values(module.sqs.queue_arns)
  secrets_arns      = values(module.secretsmanager.secret_arns)
}

# === Secrets Manager ===
module "secretsmanager" {
  source = "../../modules/secretsmanager"

  environment = var.environment
  secrets = {
    qdrant_api_key = {
      description = "Qdrant API key"
      value       = jsonencode({ api_key = var.qdrant_api_key })
    }
  }
}

# === Lambda ===
module "lambda" {
  source = "../../modules/lambda"

  environment     = var.environment
  lambda_role_arn = module.iam.lambda_role_arn
  build_dir       = "${path.module}/../../build"

  functions = {
    ingest = {
      handler     = "handler.lambda_handler"
      timeout     = 30
      memory_size = 256
      environment = {
        AWS_ENDPOINT_URL      = var.aws_internal_endpoint
        AWS_EXTERNAL_ENDPOINT = var.aws_external_endpoint
        AWS_REGION            = var.aws_region
        SQS_INPUT_URL         = module.sqs.queue_urls["input"]
        S3_AUDIO_INPUT        = module.s3.bucket_names["audio_input"]
      }
    }
    dispatcher = {
      handler     = "handler.lambda_handler"
      timeout     = 30
      memory_size = 256
      environment = {
        AWS_ENDPOINT_URL   = var.aws_internal_endpoint
        AWS_REGION         = var.aws_region
        ENVIRONMENT        = var.environment
      }
    }
    transcribe = {
      handler     = "handler.lambda_handler"
      timeout     = 60
      memory_size = 256
      environment = {
        AWS_ENDPOINT_URL     = var.aws_internal_endpoint
        AWS_REGION           = var.aws_region
        S3_TRANSCRIPTS       = module.s3.bucket_names["transcripts"]
        TRANSCRIBE_LANGUAGE  = var.transcribe_language
      }
    }
    formalize = {
      handler     = "handler.lambda_handler"
      timeout     = 60
      memory_size = 512
      environment = {
        AWS_ENDPOINT_URL          = var.aws_internal_endpoint
        AWS_REGION                = var.aws_region
        OLLAMA_URL                = var.ollama_url
        OLLAMA_FORMALIZE_MODEL    = var.ollama_formalize_model
      }
    }
    execute = {
      handler     = "handler.lambda_handler"
      timeout     = 120
      memory_size = 1024
      environment = {
        AWS_ENDPOINT_URL          = var.aws_internal_endpoint
        AWS_REGION                = var.aws_region
        OLLAMA_URL                = var.ollama_url
        OLLAMA_EXECUTE_MODEL      = var.ollama_execute_model
        OLLAMA_EMBED_MODEL        = var.ollama_embed_model
        QDRANT_URL                = var.qdrant_url
        QDRANT_COLLECTION         = var.qdrant_collection
        QDRANT_API_KEY_SECRET     = "qdrant_api_key-${var.environment}"
      }
    }
    tts = {
      handler     = "handler.lambda_handler"
      timeout     = 120
      memory_size = 512
      environment = {
        AWS_ENDPOINT_URL   = var.aws_internal_endpoint
        AWS_REGION         = var.aws_region
        TTS_SERVICE_URL    = var.tts_service_url
        S3_AUDIO_OUTPUT    = module.s3.bucket_names["audio_output"]
        SQS_OUTPUT_URL     = module.sqs.queue_urls["output"]
      }
    }
    get_result = {
      handler     = "handler.lambda_handler"
      timeout     = 30
      memory_size = 256
      environment = {
        AWS_ENDPOINT_URL      = var.aws_internal_endpoint
        AWS_EXTERNAL_ENDPOINT = var.aws_external_endpoint
        AWS_REGION            = var.aws_region
        S3_AUDIO_OUTPUT       = module.s3.bucket_names["audio_output"]
      }
    }
    index_documents = {
      handler     = "handler.lambda_handler"
      timeout     = 300
      memory_size = 1024
      environment = {
        AWS_ENDPOINT_URL      = var.aws_internal_endpoint
        AWS_REGION            = var.aws_region
        OLLAMA_URL            = var.ollama_url
        OLLAMA_EMBED_MODEL    = var.ollama_embed_model
        QDRANT_URL            = var.qdrant_url
        QDRANT_COLLECTION     = var.qdrant_collection
        QDRANT_API_KEY_SECRET = "qdrant_api_key-${var.environment}"
        S3_RAG_DOCS           = module.s3.bucket_names["rag_docs"]
      }
    }
  }
}

# === Event Source Mapping: SQS (input) → dispatcher ===
resource "aws_lambda_event_source_mapping" "input_to_dispatcher" {
  event_source_arn = module.sqs.queue_arns["input"]
  function_name    = module.lambda.function_arns["dispatcher"]
  batch_size       = 1
  enabled          = true
}

# === Event Source Mapping: SQS (tts) → tts ===
resource "aws_lambda_event_source_mapping" "tts_to_lambda" {
  event_source_arn = module.sqs.queue_arns["tts"]
  function_name    = module.lambda.function_arns["tts"]
  batch_size       = 1
  enabled          = true
}

# === Step Functions ===
module "stepfunctions" {
  source = "../../modules/stepfunctions"

  environment          = var.environment
  sfn_role_arn         = module.iam.sfn_role_arn
  lambda_function_arns = module.lambda.function_arns
  sqs_tts_url          = module.sqs.queue_urls["tts"]
}

# === API Gateway ===
module "apigateway" {
  source = "../../modules/apigateway"

  environment          = var.environment
  lambda_function_arns = module.lambda.function_arns
}