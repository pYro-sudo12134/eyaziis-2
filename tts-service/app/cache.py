import hashlib
import json
import redis.asyncio as redis
from app.config import settings

class TTSCache:
    def __init__(self):
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=False)
    
    def _key(self, text: str, voice: str, speed: float, volume: float, pitch: float, fmt: str) -> str:
        payload = json.dumps({
            "text": text,
            "voice": voice,
            "speed": speed,
            "volume": volume,
            "pitch": pitch,
            "format": fmt,
        }, sort_keys=True, ensure_ascii=False)
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return f"tts:cache:{digest}"
    
    async def get(self, text: str, voice: str, speed: float, volume: float, pitch: float, fmt: str) -> bytes | None:
        key = self._key(text, voice, speed, volume, pitch, fmt)
        return await self.client.get(key)
    
    async def set(self, text: str, voice: str, speed: float, volume: float, pitch: float, fmt: str, audio: bytes) -> None:
        key = self._key(text, voice, speed, volume, pitch, fmt)
        await self.client.setex(key, settings.CACHE_TTL_SECONDS, audio)

cache = TTSCache()