import uuid
from abc import ABC, abstractmethod
from typing import List, Optional

from src.reasoning.domain.models import (
    EvaluationContext,
    CampaignEvaluation,
    EvaluationId
)


class ICampaignReasoningService(ABC):
    """
    Application façade for Campaign Reasoning.
    Orchestrates the various reasoning engines to produce a complete CampaignEvaluation.
    This service contains no business logic itself, only coordination.
    """
    @abstractmethod
    def evaluate_campaign(self, context: EvaluationContext) -> CampaignEvaluation:
        pass


class ICampaignEvaluationRepository(ABC):
    """
    Repository interface for persisting CampaignEvaluations.
    Defines the persistence boundary for the Campaign Reasoning bounded context.
    """

    @abstractmethod
    async def save(self, evaluation: CampaignEvaluation) -> None:
        """
        Persists a new CampaignEvaluation.
        """
        pass

    @abstractmethod
    async def update(self, evaluation: CampaignEvaluation) -> None:
        """
        Updates an existing CampaignEvaluation.
        """
        pass

    @abstractmethod
    async def get_by_id(self, evaluation_id: EvaluationId) -> CampaignEvaluation:
        """
        Retrieves a CampaignEvaluation by its unique EvaluationId.
        Raises an exception if not found.
        """
        pass

    @abstractmethod
    async def get_latest_for_campaign(self, campaign_id: uuid.UUID) -> Optional[CampaignEvaluation]:
        """
        Retrieves the most recent CampaignEvaluation for a given campaign.
        Returns None if no evaluations exist for the campaign.
        """
        pass

    @abstractmethod
    async def list_for_campaign(self, campaign_id: uuid.UUID) -> List[CampaignEvaluation]:
        """
        Retrieves all CampaignEvaluations associated with a given campaign.
        """
        pass
