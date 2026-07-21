import time
import httpx
from typing import Any
from pydantic import ValidationError

from src.config.ai_settings import AISettings
from src.intelligence.schemas.ai_models import AIRequest, AIResponse
from src.intelligence.providers.base import BaseProvider
from src.intelligence.providers.ollama.client import OllamaClient
from src.intelligence.exceptions.ai import (
    AIProviderError,
    AIConnectionError,
    AITimeoutError,
    AIResponseValidationError,
    ModelNotAvailableError,
)

class OllamaProvider(BaseProvider):
    """
    Concrete implementation of IAIProvider for Ollama.
    Acts purely as an adapter, translating AIRequest to Ollama API payloads
    and translating responses/exceptions.
    """
    def __init__(self, settings: AISettings, http_client: httpx.AsyncClient):
        self._settings = settings
        self._base_url = self._settings.ollama_host.rstrip('/')
        self._client = OllamaClient(http_client)

    @property
    def provider_id(self) -> str:
        return "ollama"

    async def _do_generate(self, request: AIRequest) -> AIResponse:
        url = f"{self._base_url}/api/generate"
        
        # Build payload mapping AIRequest to Ollama API
        payload: dict[str, Any] = {
            "model": self._settings.ollama_model,
            "prompt": request.prompt,
            "stream": False,
            "options": {}
        }
        
        if request.system_prompt:
            payload["system"] = request.system_prompt
            
        temperature = request.temperature if request.temperature is not None else self._settings.ai_temperature
        if temperature is not None:
            payload["options"]["temperature"] = temperature
            
        if request.max_tokens is not None:
            payload["options"]["num_predict"] = request.max_tokens

        # Support structured output via JSON Schema format
        if request.response_schema is not None:
            payload["format"] = request.response_schema.schema()

        timeout = self._settings.ai_timeout_seconds
        
        # Execute request (measuring latency for AIResponse)
        start_time = time.time()
        raw_response = await self._client.generate(url, payload, timeout)
        latency_ms = int((time.time() - start_time) * 1000)

        # Parse response
        text = raw_response.get("response", "")
        prompt_tokens = raw_response.get("prompt_eval_count", 0)
        completion_tokens = raw_response.get("eval_count", 0)
        
        structured_output = None
        if request.response_schema is not None:
            # Parse the string into the Pydantic model
            # This can raise ValidationError, which we catch in _translate_exception
            structured_output = request.response_schema.parse_raw(text)

        return AIResponse(
            text=text,
            structured_output=structured_output,
            provider=self.provider_id,
            model=self._settings.ollama_model,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens if (prompt_tokens and completion_tokens) else None,
            raw_response=raw_response
        )

    def _translate_exception(self, e: Exception) -> Exception:
        """
        Translates native httpx and pydantic exceptions to standard AI exceptions.
        """
        if isinstance(e, httpx.TimeoutException):
            return AITimeoutError(f"Ollama request timed out: {e}")
        elif isinstance(e, httpx.ConnectError):
            return AIConnectionError(f"Failed to connect to Ollama at {self._settings.ollama_host}: {e}")
        elif isinstance(e, httpx.HTTPStatusError):
            if e.response.status_code == 404:
                return ModelNotAvailableError(f"Model '{self._settings.ollama_model}' not found in Ollama: {e.response.text}")
            return AIProviderError(f"Ollama returned HTTP {e.response.status_code}: {e.response.text}")
        elif isinstance(e, ValidationError):
            return AIResponseValidationError(f"Ollama failed to return valid JSON matching the requested schema: {e}")
        
        return AIProviderError(f"Unexpected error from Ollama: {e}")
