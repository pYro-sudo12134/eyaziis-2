import time
import redis.asyncio as redis
from fastapi import HTTPException, Request
from app.config import settings

class RateLimiter:
    def __init__(self):
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    async def check(self, request: Request) -> None:
        # Ключ по IP
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