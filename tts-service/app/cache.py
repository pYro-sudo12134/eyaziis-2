import hashlib
import json
import redis.asyncio as redis
from app.config import settings


class TTSCache:
    _client = None

    @property
    def client(self):
        if self._client is None:
            self._client = redis.from_url(settings.REDIS_URL, decode_responses=False)
        return self._client

    def _key(self, text, voice, speed, volume, pitch, fmt):
        payload = json.dumps(
            {
                "text": text,
                "voice": voice,
                "speed": speed,
                "volume": volume,
                "pitch": pitch,
                "format": fmt,
            },
            sort_keys=True,
            ensure_ascii=False,
        )
        return f"tts:cache:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"

    async def get(self, text, voice, speed, volume, pitch, fmt):
        return await self.client.get(self._key(text, voice, speed, volume, pitch, fmt))

    async def set(self, text, voice, speed, volume, pitch, fmt, audio):
        await self.client.setex(
            self._key(text, voice, speed, volume, pitch, fmt),
            settings.CACHE_TTL_SECONDS,
            audio,
        )


cache = TTSCache()
