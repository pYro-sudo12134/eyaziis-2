import logging
import requests
from shared.config import config

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or config.OLLAMA_URL
    
    def chat(
        self,
        model: str,
        messages: list[dict],
        format: str = None,
        temperature: float = 0.7,
        timeout: int = 120,
    ) -> str:
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if format:
            payload["format"] = format
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    
    def embed(self, text: str, model: str = None, timeout: int = 30) -> list[float]:
        model = model or config.OLLAMA_EMBED_MODEL
        response = requests.post(
            f"{self.base_url}/api/embeddings",
            json={"model": model, "prompt": text},
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()["embedding"]


ollama = OllamaClient()