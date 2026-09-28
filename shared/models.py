from pydantic import BaseModel


class IngestMessage(BaseModel):
    request_id: str
    input_type: str  # "text" | "audio"
    text: str | None = None
    s3_uri: str | None = None
    voice: str = "ru_RU-irina-medium"
    speed: float = 1.0
    volume: float = 1.0
    pitch: float = 1.0
    format: str = "mp3"


class FormalizedCommand(BaseModel):
    command: str
    params: dict


class AnswerResult(BaseModel):
    text: str
    voice: str = "ru_RU-irina-medium"
    speed: float = 1.0
    volume: float = 1.0
    pitch: float = 1.0
    format: str = "mp3"
