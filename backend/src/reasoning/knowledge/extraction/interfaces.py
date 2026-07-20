from typing import List, Protocol
import uuid

from src.reasoning.extraction.models import CampaignEntityDocument
from src.reasoning.eligibility.models import EligibilityAssessment
from src.reasoning.worth_it.models import WorthItAssessment
from src.reasoning.recommendation.models import Recommendation
from src.reasoning.knowledge.models import KnowledgeEntry


class IKnowledgeExtractionRule(Protocol):
    """
    Protocol for a rule that evaluates a campaign to extract a specific category of deterministic knowledge.
    Must never inspect historical campaigns or persist data.
    """
    
    def evaluate(
        self,
        evaluation_id: uuid.UUID,
        campaign_name: str,
        document: CampaignEntityDocument,
        eligibility: EligibilityAssessment,
        worth_it: WorthItAssessment,
        recommendation: Recommendation
    ) -> List[KnowledgeEntry]:
        """
        Extracts knowledge entries for a single campaign.
        """
        ...


class IKnowledgeExtractionEngine(Protocol):
    """
    Protocol for extracting deterministic knowledge from a single campaign evaluation.
    """
    
    def extract(
        self,
        evaluation_id: uuid.UUID,
        campaign_name: str,
        document: CampaignEntityDocument,
        eligibility: EligibilityAssessment,
        worth_it: WorthItAssessment,
        recommendation: Recommendation
    ) -> List[KnowledgeEntry]:
        """
        Coordinates rules to produce immutable candidate knowledge entries.
        """
        ...
