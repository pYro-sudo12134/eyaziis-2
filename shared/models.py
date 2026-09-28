from pydantic import BaseModel, Field
from typing import Optional


class IngestMessage(BaseModel):
    request_id: str
    input_type: str  # "text" | "audio"
    text: Optional[str] = None
    s3_uri: Optional[str] = None
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
