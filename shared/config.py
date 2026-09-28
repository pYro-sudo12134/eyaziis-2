import os


class Config:
    AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localstack:4566")
    AWS_EXTERNAL_ENDPOINT = os.getenv("AWS_EXTERNAL_ENDPOINT", "http://localhost:4566")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "test")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")

    DYNAMODB_REQUESTS_TABLE = os.getenv("DYNAMODB_REQUESTS_TABLE", "requests")

    SQS_INPUT_URL = os.getenv("SQS_INPUT_URL", "")
    SQS_TTS_URL = os.getenv("SQS_TTS_URL", "")
    SQS_OUTPUT_URL = os.getenv("SQS_OUTPUT_URL", "")

    S3_AUDIO_INPUT = os.getenv("S3_AUDIO_INPUT", "audio-input")
    S3_AUDIO_OUTPUT = os.getenv("S3_AUDIO_OUTPUT", "audio-output")
    S3_TRANSCRIPTS = os.getenv("S3_TRANSCRIPTS", "transcripts")
    S3_RAG_DOCS = os.getenv("S3_RAG_DOCS", "rag-documents")

    STATE_MACHINE_ARN = os.getenv("STATE_MACHINE_ARN", "")

    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama1:11434")
    OLLAMA_FORMALIZE_MODEL = os.getenv("OLLAMA_FORMALIZE_MODEL", "qwen2.5:0.5b")
    OLLAMA_EXECUTE_MODEL = os.getenv("OLLAMA_EXECUTE_MODEL", "qwen2.5:3b")
    OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

    QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "literature")
    QDRANT_API_KEY_SECRET = os.getenv("QDRANT_API_KEY_SECRET", "")

    TTS_SERVICE_URL = os.getenv("TTS_SERVICE_URL", "http://tts-service:8000")

    TRANSCRIBE_LANGUAGE = os.getenv("TRANSCRIBE_LANGUAGE", "ru-RU")
    TRANSCRIBE_POLL_INTERVAL = int(os.getenv("TRANSCRIBE_POLL_INTERVAL", "5"))
    TRANSCRIBE_MAX_ATTEMPTS = int(os.getenv("TRANSCRIBE_MAX_ATTEMPTS", "60"))

    SECRETS_MANAGER_ENABLED = os.getenv("SECRETS_MANAGER_ENABLED", "true").lower() == "true"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
    STATE_MACHINE_ARN_PARAM = os.getenv(
        "STATE_MACHINE_ARN_PARAM", f"/pipeline/{ENVIRONMENT}/state_machine_arn"
    )


config = Config()
