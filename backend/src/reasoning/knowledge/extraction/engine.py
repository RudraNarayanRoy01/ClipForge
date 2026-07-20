from typing import List, Set
import uuid
from dataclasses import replace

from .interfaces import IKnowledgeExtractionEngine, IKnowledgeExtractionRule
from src.reasoning.extraction.models import CampaignEntityDocument
from src.reasoning.eligibility.models import EligibilityAssessment
from src.reasoning.worth_it.models import WorthItAssessment
from src.reasoning.recommendation.models import Recommendation
from src.reasoning.knowledge.models import (
    KnowledgeEntry,
    KnowledgeEvidence,
    KnowledgeSource,
    CampaignEvaluationReference
)


class DefaultKnowledgeExtractionEngine(IKnowledgeExtractionEngine):
    """
    Coordinates rules to deterministically extract knowledge assertions from a single campaign evaluation.
    """
    
    def __init__(self, rules: List[IKnowledgeExtractionRule]):
        self._rules = rules

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
        Extracts candidate knowledge entries across all rules and removes identical duplicates.
        Centralizes the creation of KnowledgeEvidence.
        """
        
        all_entries: List[KnowledgeEntry] = []
        
        # Centralize evidence creation for consistency across all extracted candidate assertions
        reference = CampaignEvaluationReference(evaluation_id=evaluation_id, campaign_name=campaign_name)
        common_evidence = KnowledgeEvidence(
            source=KnowledgeSource.CAMPAIGN_EVALUATION,
            description=f"Candidate observation extracted during evaluation of campaign '{campaign_name}'.",
            reference=reference
        )
        
        # Invoke all independent rules
        for rule in self._rules:
            entries = rule.evaluate(
                evaluation_id=evaluation_id,
                campaign_name=campaign_name,
                document=document,
                eligibility=eligibility,
                worth_it=worth_it,
                recommendation=recommendation
            )
            
            # Inject centralized evidence into the immutable knowledge entries
            for entry in entries:
                entry_with_evidence = replace(entry, evidence=[common_evidence])
                all_entries.append(entry_with_evidence)
            
        # Deduplicate identical entries
        return self._deduplicate(all_entries)
        
    def _deduplicate(self, entries: List[KnowledgeEntry]) -> List[KnowledgeEntry]:
        """
        Removes obvious identical duplicate assertions generated during the same pass.
        This does NOT perform semantic merging, only exact-match deduplication.
        """
        unique_signatures: Set[str] = set()
        deduplicated: List[KnowledgeEntry] = []
        
        for entry in entries:
            # We base the unique signature on the core business values of the knowledge assertion
            signature = f"{entry.category.name}|{entry.subject}|{entry.value}|{entry.confidence.name}"
            
            if signature not in unique_signatures:
                unique_signatures.add(signature)
                deduplicated.append(entry)
                
        return deduplicated
