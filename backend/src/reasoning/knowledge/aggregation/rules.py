from typing import Sequence, List, Set
from dataclasses import replace

from src.reasoning.knowledge.models import KnowledgeEntry, KnowledgeConfidence, KnowledgeEvidence
from .interfaces import IKnowledgeAggregationRule, IConfidencePolicy


class DefaultConfidencePolicy(IConfidencePolicy):
    """
    Deterministically determines the confidence of a knowledge assertion based on 
    how many independent candidate observations have been accumulated.
    """
    
    def evaluate(self, entries: Sequence[KnowledgeEntry]) -> KnowledgeConfidence:
        count = len(entries)
        
        if count >= 4:
            return KnowledgeConfidence.HIGH
        elif count >= 2:
            return KnowledgeConfidence.MEDIUM
        else:
            return KnowledgeConfidence.LOW


class ConfidenceAggregationRule(IKnowledgeAggregationRule):
    """
    Evolves knowledge confidence by delegating to a policy object.
    Maintains separation between the aggregation orchestration and the actual confidence thresholds.
    """
    
    def __init__(self, policy: IConfidencePolicy):
        self._policy = policy
        
    def apply(self, current: KnowledgeEntry, candidates: Sequence[KnowledgeEntry]) -> KnowledgeEntry:
        new_confidence = self._policy.evaluate(candidates)
        return replace(current, confidence=new_confidence)


class EvidenceAggregationRule(IKnowledgeAggregationRule):
    """
    Accumulates real observational evidence from all candidate knowledge entries.
    Merges unique evidence to preserve provenance without creating synthetic aggregation records.
    """
    
    def apply(self, current: KnowledgeEntry, candidates: Sequence[KnowledgeEntry]) -> KnowledgeEntry:
        unique_evidence: Set[KnowledgeEvidence] = set()
        merged_evidence: List[KnowledgeEvidence] = []
        
        # Accumulate all evidence from the current base entry (if any) and candidates
        all_sources = list(current.evidence)
        for candidate in candidates:
            all_sources.extend(candidate.evidence)
            
        for evidence in all_sources:
            if evidence not in unique_evidence:
                unique_evidence.add(evidence)
                merged_evidence.append(evidence)
                
        return replace(current, evidence=merged_evidence)
