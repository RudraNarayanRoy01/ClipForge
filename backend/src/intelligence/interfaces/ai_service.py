from typing import Protocol
from src.intelligence.schemas.ai_models import AIRequest, AIResponse

class IAIService(Protocol):
    """
    Central orchestration contract for AI operations.
    Business services communicate EXCLUSIVELY with this layer.
    It operates exclusively on AIRequest and returns AIResponse.
    """
    async def execute_request(self, request: AIRequest) -> AIResponse:
        ...
