import re
from pydantic import ValidationError

from src.intelligence.interfaces.ai_service import IAIService
from src.intelligence.schemas.ai_models import AIExecutionCommand, AIResponse, AIRequest
from src.intelligence.prompts.manager import PromptManager
from src.intelligence.providers.factory import ProviderFactory
from src.intelligence.exceptions.ai import AIResponseValidationError

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
        
        # 4. Execute request
        response = await provider.generate(request)
        
        # 5. Canonical structured output validation
        if command.response_schema:
            try:
                # If provider natively returned a pre-parsed data structure (e.g., via Tool Calling/JSON Mode)
                if isinstance(response.structured_output, (dict, list)):
                    response.structured_output = command.response_schema.parse_obj(response.structured_output)
                elif response.text:
                    text = response.text.strip()
                    # Defensively strip markdown formatting (case-insensitive for language identifier)
                    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.IGNORECASE)
                    text = re.sub(r'\s*```$', '', text)
                    response.structured_output = command.response_schema.parse_raw(text.strip())
                else:
                    raise AIResponseValidationError("Provider returned empty response when structured output was expected.")
            except ValidationError as e:
                raise AIResponseValidationError(f"Failed to validate provider output against schema: {e}") from e
            except (ValueError, TypeError) as e:
                raise AIResponseValidationError(f"Failed to parse provider output as JSON: {e}") from e
                
        return response
