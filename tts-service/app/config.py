from pathlib import Path
import os

class Settings:
    VOICES_DIR: Path = Path("/app/voices")
    PIPER_BIN: str = "/usr/local/bin/piper"
    FFMPEG_BIN: str = "/usr/bin/ffmpeg"
    
    DEFAULT_VOICE: str = "ru_RU-irina-medium"
    DEFAULT_SPEED: float = 1.0
    DEFAULT_VOLUME: float = 1.0
    DEFAULT_PITCH: float = 1.0
    DEFAULT_FORMAT: str = "mp3"
    MAX_TEXT_LENGTH: int = 5000

    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS",
        "*"
    ).split(",")

settings = Settings()