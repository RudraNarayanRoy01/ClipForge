from src.intelligence.interfaces.ai_service import IAIService
from src.intelligence.schemas.ai_models import AIExecutionCommand, AIResponse, AIRequest
from src.intelligence.prompts.manager import PromptManager
from src.intelligence.providers.factory import ProviderFactory

class DefaultAIService(IAIService):
    """
    Canonical orchestration layer for all AI interactions in ClipForge.
    Coordinates prompt rendering and provider execution.
    """
    def __init__(self, prompt_manager: PromptManager, provider_factory: ProviderFactory):
        self._prompt_manager = prompt_manager
        self._provider_factory = provider_factory

    async def execute(self, command: AIExecutionCommand) -> AIResponse:
        """
        Executes a high-level AIExecutionCommand by rendering the prompt
        and dispatching to the configured AI provider.
        """
        # 1. Render prompt via PromptManager
        rendered_prompt = self._prompt_manager.render(
            prompt_identifier=command.prompt_identifier,
            **command.template_variables
        )
        
        # 2. Construct infrastructure-level AIRequest
        request = AIRequest(
            prompt=rendered_prompt.text,
            response_schema=command.response_schema,
            temperature=rendered_prompt.metadata.default_temperature
        )
        
        # 3. Resolve the active provider via ProviderFactory
        provider = self._provider_factory.create_provider()
        
        # 4. Execute and return response
        return await provider.generate(request)
