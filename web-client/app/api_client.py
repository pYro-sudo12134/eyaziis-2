import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class ApiClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def ask_text(self, payload: dict[str, Any]) -> dict:
        r = await self._client.post(settings.ask_url, json=payload)
        r.raise_for_status()
        return r.json()

    async def ask_audio(self, payload: dict[str, Any]) -> dict:
        r = await self._client.post(settings.ask_audio_url, json=payload)
        r.raise_for_status()
        return r.json()

    async def get_result(self, request_id: str) -> dict:
        r = await self._client.get(settings.result_url(request_id))
        r.raise_for_status()
        return r.json()

    async def get_voices(self) -> dict:
        r = await self._client.get(f"{settings.TTS_SERVICE_URL}/voices")
        r.raise_for_status()
        return r.json()


api_client = ApiClient()