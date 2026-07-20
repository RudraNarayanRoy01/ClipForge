from typing import List
import uuid

from .interfaces import IKnowledgeExtractionRule
from src.reasoning.extraction.models import CampaignEntityDocument
from src.reasoning.eligibility.models import EligibilityAssessment
from src.reasoning.worth_it.models import WorthItAssessment
from src.reasoning.recommendation.models import Recommendation
from src.reasoning.knowledge.models import (
    KnowledgeEntry,
    KnowledgeCategory,
    KnowledgeConfidence,
)


class CreatorKnowledgeRule(IKnowledgeExtractionRule):
    """
    Extracts creator-related candidate knowledge assertions.
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
        entries: List[KnowledgeEntry] = []

        for req in document.requirements:
            entries.append(
                KnowledgeEntry(
                    category=KnowledgeCategory.CREATOR,
                    subject="Creator Quality Pattern",
                    value=f"Observation suggests creator expectations include: {req.original_text}",
                    confidence=KnowledgeConfidence.LOW
                )
            )

        return entries


class PlatformKnowledgeRule(IKnowledgeExtractionRule):
    """
    Extracts platform-related candidate knowledge assertions.
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
        entries: List[KnowledgeEntry] = []

        for platform in document.platforms:
            entries.append(
                KnowledgeEntry(
                    category=KnowledgeCategory.PLATFORM,
                    subject="Platform Requirement Pattern",
                    value=f"Candidate observation: Targeting '{platform.original_text}' may entail platform-specific content rules.",
                    confidence=KnowledgeConfidence.LOW
                )
            )

        return entries


class RestrictionKnowledgeRule(IKnowledgeExtractionRule):
    """
    Extracts restriction-related candidate knowledge assertions.
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
        entries: List[KnowledgeEntry] = []

        for restriction in document.restrictions:
            entries.append(
                KnowledgeEntry(
                    category=KnowledgeCategory.RESTRICTION,
                    subject="Restriction Risk Pattern",
                    value=f"Observation indicates that restriction '{restriction.original_text}' might elevate rejection risk.",
                    confidence=KnowledgeConfidence.LOW
                )
            )

        return entries


class RewardKnowledgeRule(IKnowledgeExtractionRule):
    """
    Extracts reward-related candidate knowledge assertions.
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
        entries: List[KnowledgeEntry] = []

        for reward in document.rewards:
            entries.append(
                KnowledgeEntry(
                    category=KnowledgeCategory.REWARD,
                    subject="Reward Tier Observation",
                    value=f"Observed reward pattern ({reward.original_text}) suggests a potential premium payout structure.",
                    confidence=KnowledgeConfidence.LOW
                )
            )

        return entries


class RecommendationKnowledgeRule(IKnowledgeExtractionRule):
    """
    Extracts knowledge assertions derived from the final recommendation.
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
        entries: List[KnowledgeEntry] = []

        for reason in recommendation.rationale.reasons:
            entries.append(
                KnowledgeEntry(
                    category=KnowledgeCategory.CAMPAIGN,
                    subject="Decision Pattern Insight",
                    value=f"Observation: Decision '{recommendation.decision.name}' was influenced by '{reason.code}'. This may indicate a recurring workflow pattern.",
                    confidence=KnowledgeConfidence.LOW
                )
            )

        return entries
