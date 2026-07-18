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
    EvaluationMetadata,
    RecommendationConfidence,
    RecommendationPriority,
    RecommendationExplanation,
    EvaluationSummary
)

__all__ = [
    # Factory (Composition Root)
    "CampaignReasoningFactory",
    
    # Application Services
    "ICampaignReasoningService",
    
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
    "EvaluationMetadata",
    "RecommendationConfidence",
    "RecommendationPriority",
    "RecommendationExplanation",
    "EvaluationSummary"
]
