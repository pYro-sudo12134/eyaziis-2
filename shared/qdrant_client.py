import logging

import requests

from shared.config import config
from shared.secrets import get_qdrant_api_key

logger = logging.getLogger(__name__)


class QdrantClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or config.QDRANT_URL
        self.collection = config.QDRANT_COLLECTION

    def _headers(self) -> dict:
        api_key = get_qdrant_api_key()
        if api_key:
            return {"api-key": api_key}
        return {}

    def ensure_collection(self, vector_size: int = 768) -> None:
        url = f"{self.base_url}/collections/{self.collection}"
        response = requests.get(url, headers=self._headers(), timeout=10)

        if response.status_code == 404:
            logger.info(f"Creating collection: {self.collection}")
            requests.put(
                url,
                json={
                    "vectors": {
                        "size": vector_size,
                        "distance": "Cosine",
                    }
                },
                headers=self._headers(),
                timeout=30,
            )

    def upsert(self, points: list[dict]) -> None:
        url = f"{self.base_url}/collections/{self.collection}/points"
        response = requests.put(
            url,
            json={"points": points},
            headers=self._headers(),
            timeout=60,
        )
        response.raise_for_status()

    def search(self, vector: list[float], top_k: int = 3) -> list[dict]:
        url = f"{self.base_url}/collections/{self.collection}/points/search"
        response = requests.post(
            url,
            json={
                "vector": vector,
                "limit": top_k,
                "with_payload": True,
            },
            headers=self._headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["result"]


qdrant = QdrantClient()
