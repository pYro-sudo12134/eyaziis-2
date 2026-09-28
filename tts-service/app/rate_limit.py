import time

import redis.asyncio as redis
from app.config import settings
from fastapi import HTTPException, Request


class RateLimiter:
    _client = None

    @property
    def client(self):
        if self._client is None:
            self._client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        return self._client

    async def check(self, request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        window = int(time.time() // settings.RATE_LIMIT_WINDOW)
        key = f"tts:ratelimit:{client_ip}:{window}"

        count = await self.client.incr(key)
        if count == 1:
            await self.client.expire(key, settings.RATE_LIMIT_WINDOW)

        if count > settings.RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_WINDOW}s",
                headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW)},
            )


rate_limiter = RateLimiter()
