from src.infrastructure.di.container import Container
from src.bootstrap.modules import DIModule
from src.config.ai_settings import AISettings
from src.intelligence.providers.capabilities import IAIProvider
from src.intelligence.providers.ollama.provider import OllamaProvider
from src.domain.ports import ILLMReasoningEngine
from src.infrastructure.ai_adapter import AIProviderLLMEngineAdapter
from src.intelligence.services.campaign_intelligence import CampaignIntelligenceService
from src.intelligence.interfaces.ai_service import IAIService
from src.intelligence.orchestration.default_service import DefaultAIService
from src.intelligence.prompts.manager import PromptManager
import httpx
import os

class IntelligenceModule(DIModule):
    def register(self, container: Container) -> None:
        ai_settings = AISettings()
        container.register_singleton(AISettings, ai_settings)
        
        # Register PromptManager
        pm_path = os.path.join(os.path.dirname(__file__), '..', '..', 'intelligence', 'prompts')
        container.register_singleton(PromptManager, PromptManager(base_dir=pm_path))
        
        # Register Provider (e.g. OllamaProvider as IAIProvider)
        def create_provider(c: Container) -> IAIProvider:
            return OllamaProvider(ai_settings, c.resolve(httpx.AsyncClient))
            
        container.register_factory(IAIProvider, create_provider, singleton=True)
        
        # Register Adapter to ILLMReasoningEngine
        container.register_transient(ILLMReasoningEngine, AIProviderLLMEngineAdapter)
        
        # Register DefaultAIService
        # Assuming DefaultAIService requires PromptManager and ProviderFactory. 
        # For simplicity we might just inject IAIProvider if the service is updated, 
        # but since we shouldn't redesign we'll construct it as they did before, or register transient.
        # Actually in campaigns.py it's: DefaultAIService(prompt_manager=_prompt_manager, provider_factory=_provider_factory)
        from src.intelligence.providers.factory import ProviderFactory
        container.register_singleton(ProviderFactory, ProviderFactory(ai_settings))
        container.register_transient(IAIService, DefaultAIService)
        
        # Register CampaignIntelligenceService
        def create_campaign_intelligence(c: Container) -> CampaignIntelligenceService:
            # IAIProvider acts as IStructuredOutput in this architecture
            provider = c.resolve(IAIProvider)
            ai_service = c.resolve(IAIService)
            return CampaignIntelligenceService(structured_llm=provider, ai_service=ai_service)
            
        container.register_factory(CampaignIntelligenceService, create_campaign_intelligence, singleton=False)
