from pydantic import BaseModel, Field


class SynthesizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    voice: str = Field(default="ru_RU-irina-medium")
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    volume: float = Field(default=1.0, ge=0.0, le=2.0)
    pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    format: str = Field(default="mp3", pattern="^(wav|mp3|ogg)$")


class VoiceInfo(BaseModel):
    id: str
    name: str
    gender: str
    language: str
    quality: str


class VoicesResponse(BaseModel):
    voices: list[VoiceInfo]
    default: str
    formats: list[str]
