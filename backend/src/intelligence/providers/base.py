import time
import logging
from abc import ABC, abstractmethod

from src.intelligence.schemas.ai_models import AIRequest, AIResponse

logger = logging.getLogger(__name__)

class BaseProvider(ABC):
    """
    Lightweight base class for all AI Providers.
    Responsibilities:
    - Standardized logging
    - Execution timing
    - Standardized exception translation hooks
    """
    
    @property
    @abstractmethod
    def provider_id(self) -> str:
        """The identifier of the provider (e.g., 'ollama', 'gemini')."""
        pass

    @abstractmethod
    async def _do_generate(self, request: AIRequest) -> AIResponse:
        """
        Inner method implemented by concrete providers.
        Responsible for translating AIRequest -> API payload -> AIResponse.
        """
        pass
        
    @abstractmethod
    def _translate_exception(self, e: Exception) -> Exception:
        """
        Hook for concrete providers to translate SDK/HTTP exceptions 
        into standard AIExceptions defined in src.intelligence.exceptions.ai.
        """
        pass

    async def generate(self, request: AIRequest) -> AIResponse:
        """Wrapper method that handles timing, logging, and exception translation."""
        start_time = time.time()
        success = False
        error_msg = None
        
        try:
            response = await self._do_generate(request)
            success = True
            return response
        except Exception as e:
            translated_e = self._translate_exception(e)
            error_msg = str(translated_e)
            raise translated_e from e
        finally:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_execution(duration_ms, success, error_msg)

    def _log_execution(self, duration_ms: int, success: bool, error: str | None = None) -> None:
        """Standardized logging for all providers."""
        extra = {
            "ai_provider": self.provider_id,
            "duration_ms": duration_ms,
            "success": success
        }
        if success:
            logger.info(f"AI Generation successful via {self.provider_id}", extra=extra)
        else:
            extra["error"] = error
            logger.error(f"AI Generation failed via {self.provider_id}: {error}", extra=extra)
