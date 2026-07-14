from typing import Protocol
from src.intelligence.schemas.ai_models import AIExecutionCommand, AIResponse

class IAIService(Protocol):
    """
    Central orchestration contract for AI operations.
    Business services communicate EXCLUSIVELY with this layer.
    It operates exclusively on AIExecutionCommand and returns AIResponse.
    """
    async def execute(self, command: AIExecutionCommand) -> AIResponse:
        ...
