from abc import ABC, abstractmethod

from src.reasoning.domain.models import (
    EvaluationContext,
    EligibilityResult,
    CompatibilityResult,
    SuitabilityResult,
    RiskAssessment,
    WorthItAssessment,
    RecommendationResult,
    CampaignEvaluation
)


class IEligibilityEngine(ABC):
    """
    Evaluates whether a campaign is fundamentally eligible to be processed.
    Responsible for checking hard constraints and basic requirements.
    """
    @abstractmethod
    async def evaluate(self, context: EvaluationContext) -> EligibilityResult:
        pass


class ICompatibilityEngine(ABC):
    """
    Evaluates if the campaign rules and requirements are compatible with the video content.
    Responsible for determining if the requested formats and constraints match the source.
    """
    @abstractmethod
    async def evaluate(self, context: EvaluationContext) -> CompatibilityResult:
        pass


class ISuitabilityEngine(ABC):
    """
    Evaluates how suitable the video content is for the specific campaign.
    Responsible for semantic alignment and brand voice matching.
    """
    @abstractmethod
    async def evaluate(self, context: EvaluationContext) -> SuitabilityResult:
        pass


class IRiskEngine(ABC):
    """
    Assesses potential risks associated with the campaign and video pairing.
    Responsible for flagging brand safety, copyright, and compliance issues.
    """
    @abstractmethod
    async def assess(self, context: EvaluationContext) -> RiskAssessment:
        pass


class IWorthItEngine(ABC):
    """
    Evaluates whether the expected value of the campaign justifies the effort/cost.
    Responsible for ROI estimation and prioritization scoring.
    """
    @abstractmethod
    async def evaluate(self, context: EvaluationContext) -> WorthItAssessment:
        pass


class IRecommendationEngine(ABC):
    """
    Generates the final recommendation based on the evaluation gathered so far.
    Responsible for synthesizing all preceding evaluations into a conclusive decision.
    """
    @abstractmethod
    async def generate_recommendation(
        self, 
        context: EvaluationContext,
        eligibility: EligibilityResult,
        compatibility: CompatibilityResult,
        suitability: SuitabilityResult,
        risk: RiskAssessment,
        worth_it: WorthItAssessment
    ) -> RecommendationResult:
        pass


class ICampaignReasoningService(ABC):
    """
    Application façade for Campaign Reasoning.
    Orchestrates the various reasoning engines to produce a complete CampaignEvaluation.
    This service contains no business logic itself, only coordination.
    """
    @abstractmethod
    async def evaluate_campaign(self, context: EvaluationContext) -> CampaignEvaluation:
        pass
