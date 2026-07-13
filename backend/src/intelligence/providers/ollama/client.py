import httpx
from typing import Dict, Any

class OllamaClient:
    """
    Lightweight HTTP wrapper for Ollama API.
    Request execution only. Connection management is injected to prevent 
    hidden global state and decouple lifecycle ownership.
    """
    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    async def generate(self, url: str, payload: Dict[str, Any], timeout: float) -> Dict[str, Any]:
        """
        Executes a POST request to Ollama's /api/generate endpoint.
        Raises native httpx exceptions which are translated by the Provider.
        """
        response = await self._client.post(
            url,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
