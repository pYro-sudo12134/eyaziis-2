import time
import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from app.rate_limit import RateLimiter
from app.config import settings


def make_request(ip="1.2.3.4"):
    req = MagicMock()
    req.client.host = ip
    return req


@pytest.fixture
def limiter(fake_redis):
    rl = RateLimiter()
    rl._client = fake_redis
    return rl


@pytest.mark.asyncio
async def test_blocks_over_limit(limiter):
    req = make_request()
    for _ in range(settings.RATE_LIMIT_REQUESTS):
        await limiter.check(req)
    with pytest.raises(HTTPException) as exc:
        await limiter.check(req)
    assert exc.value.status_code == 429


@pytest.mark.asyncio
async def test_limits_are_per_ip(limiter):
    a = make_request("10.0.0.1")
    b = make_request("10.0.0.2")
    for _ in range(settings.RATE_LIMIT_REQUESTS):
        await limiter.check(a)
    await limiter.check(b)


@pytest.mark.asyncio
async def test_counter_key_uses_window_bucket(limiter, fake_redis):
    """Ключ должен включать бакет окна, иначе окно не сбрасывается."""
    req = make_request("9.9.9.9")
    await limiter.check(req)
    key = next(iter(fake_redis._storage))
    window = int(time.time() // settings.RATE_LIMIT_WINDOW)
    assert key == f"tts:ratelimit:9.9.9.9:{window}"


@pytest.mark.asyncio
async def test_expire_set_only_on_first_hit(limiter, fake_redis):
    """Если expire ставить на каждом запросе — TTL будет продлеваться бесконечно."""
    req = make_request("5.5.5.5")
    await limiter.check(req)
    await limiter.check(req)
    await limiter.check(req)
    assert fake_redis.expire.await_count == 1


@pytest.mark.asyncio
async def test_no_client_host_falls_back_to_unknown(limiter, fake_redis):
    req = MagicMock()
    req.client = None
    await limiter.check(req)
    key = next(iter(fake_redis._storage))
    assert "tts:ratelimit:unknown:" in key