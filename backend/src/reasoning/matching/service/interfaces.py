from abc import ABC, abstractmethod
from typing import List

from src.domain.campaign_entities import Campaign
from src.reasoning.knowledge.models import KnowledgeEntry
from src.reasoning.matching.models import MatchingOutcome, MatchRequest
from src.reasoning.matching.rules.interfaces import MatchingContext


class IMatchingContextFactory(ABC):
    """
    Factory responsible for constructing the MatchingContext from application inputs.
    Abstracts the logic of context assembly away from the orchestration service.
    """

    @abstractmethod
    def create(
        self, 
        request: MatchRequest, 
        campaign: Campaign, 
        knowledge: List[KnowledgeEntry]
    ) -> MatchingContext:
        """
        Constructs the immutable MatchingContext.

        Args:
            request (MatchRequest): The parameters defining the match evaluation.
            campaign (Campaign): The campaign being evaluated.
            knowledge (List[KnowledgeEntry]): The relevant knowledge entries.

        Returns:
            MatchingContext: The domain state required for rule evaluation.
        """
        pass


class IMatchingService(ABC):
    """
    Orchestrates the complete matching workflow.
    Coordinates the construction of context, execution of rules (via Engine),
    and interpretation of results (via Policy) without containing business logic.
    """

    @abstractmethod
    def evaluate_match(
        self, 
        request: MatchRequest, 
        campaign: Campaign, 
        knowledge: List[KnowledgeEntry]
    ) -> MatchingOutcome:
        """
        Coordinates the evaluation of a match request against a campaign and knowledge base.

        Args:
            request (MatchRequest): The parameters defining the match evaluation.
            campaign (Campaign): The campaign being evaluated.
            knowledge (List[KnowledgeEntry]): The relevant knowledge entries.

        Returns:
            MatchingOutcome: The structured outcome encapsulating the request, result, and business decision.
            
        Raises:
            MatchingServiceError: If an orchestration error occurs.
        """
        pass
