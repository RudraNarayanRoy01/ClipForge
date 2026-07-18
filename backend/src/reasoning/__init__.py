from .factory import CampaignReasoningFactory
from .interfaces import (
    ICampaignReasoningService,
    IEligibilityEngine,
    ICompatibilityEngine,
    ISuitabilityEngine,
    IRiskEngine,
    IWorthItEngine,
    IRecommendationEngine,
    ICampaignEvaluationRepository
)
from .services.campaign_reasoning_service import DefaultCampaignReasoningService
from .domain.models import (
    EvaluationContext,
    CampaignEvaluation,
    EligibilityResult,
    CompatibilityResult,
    SuitabilityResult,
    RiskAssessment,
    WorthItAssessment,
    RecommendationResult,
    EvaluationId,
    EvaluationStatus,
    EvaluationMetadata
)

__all__ = [
    # Factory (Composition Root)
    "CampaignReasoningFactory",
    
    # Application Services
    "ICampaignReasoningService",
    "DefaultCampaignReasoningService",
    
    # Engines
    "IEligibilityEngine",
    "ICompatibilityEngine",
    "ISuitabilityEngine",
    "IRiskEngine",
    "IWorthItEngine",
    "IRecommendationEngine",
    
    # Persistence
    "ICampaignEvaluationRepository",
    
    # Domain Models
    "EvaluationContext",
    "CampaignEvaluation",
    "EligibilityResult",
    "CompatibilityResult",
    "SuitabilityResult",
    "RiskAssessment",
    "WorthItAssessment",
    "RecommendationResult",
    "EvaluationId",
    "EvaluationStatus",
    "EvaluationMetadata"
]
