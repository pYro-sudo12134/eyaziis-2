import os
from pathlib import Path


class Settings:
    API_GATEWAY_URL: str = os.getenv("API_GATEWAY_URL", "http://localstack:4566")
    API_ID: str = os.getenv("API_ID", "")
    API_STAGE: str = os.getenv("API_STAGE", "dev")

    TTS_SERVICE_URL: str = os.getenv("TTS_SERVICE_URL", "http://tts-service:8000")
    FFMPEG_BIN: str = os.getenv("FFMPEG_BIN", "/usr/bin/ffmpeg")

    HTTP_TIMEOUT: float = float(os.getenv("HTTP_TIMEOUT", "30"))
    POLL_TIMEOUT: int = int(os.getenv("POLL_TIMEOUT", "180"))

    TEMPLATES_DIR: Path = Path(__file__).parent / "templates"
    STATIC_DIR: Path = Path(__file__).parent.parent / "static"

    def _api_url(self, path: str) -> str:
        if not self.API_ID:
            raise RuntimeError("API_ID is not configured")
        return (
            f"{self.API_GATEWAY_URL}"
            f"/restapis/{self.API_ID}"
            f"/{self.API_STAGE}"
            f"/_user_request_/{path}"
        )

    @property
    def ask_url(self) -> str:
        return self._api_url("ask")

    @property
    def ask_audio_url(self) -> str:
        return self._api_url("ask-audio")

    def result_url(self, request_id: str) -> str:
        return self._api_url(f"result/{request_id}")


settings = Settings()
