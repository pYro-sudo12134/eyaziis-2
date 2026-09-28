import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def fake_redis():
    client = MagicMock()
    storage = {}

    async def _get(key):
        return storage.get(key)

    async def _setex(key, ttl, value):
        storage[key] = value

    async def _incr(key):
        storage[key] = storage.get(key, 0) + 1
        return storage[key]

    async def _expire(key, ttl):
        return True

    async def _ping():
        return True

    client.get = AsyncMock(side_effect=_get)
    client.setex = AsyncMock(side_effect=_setex)
    client.incr = AsyncMock(side_effect=_incr)
    client.expire = AsyncMock(side_effect=_expire)
    client.ping = AsyncMock(side_effect=_ping)
    client._storage = storage
    return client


@pytest.fixture
def app_client(fake_redis):
    from app import cache as cache_module
    from app import rate_limit as rl_module

    cache_module.cache._client = fake_redis
    rl_module.rate_limiter._client = fake_redis

    from app.main import app
    with TestClient(app) as client:
        yield client

    cache_module.cache._client = None
    rl_module.rate_limiter._client = None