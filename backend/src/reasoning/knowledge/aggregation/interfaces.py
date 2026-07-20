from abc import ABC, abstractmethod
from typing import Sequence

from src.reasoning.knowledge.models import KnowledgeEntry, KnowledgeConfidence


class IConfidencePolicy(ABC):
    """
    Determines how knowledge confidence evolves based on accumulated observations.
    Separates the policy (thresholds) from the aggregation orchestration.
    """
    
    @abstractmethod
    def evaluate(self, entries: Sequence[KnowledgeEntry]) -> KnowledgeConfidence:
        """
        Evaluates the aggregated confidence for a group of identical knowledge assertions.
        
        Args:
            entries: A group of candidate KnowledgeEntry objects representing the same observation.
            
        Returns:
            KnowledgeConfidence: The newly evolved confidence level.
        """
        pass


class IKnowledgeAggregationRule(ABC):
    """
    Independent aggregation rule for transforming candidate knowledge assertions.
    """
    
    @abstractmethod
    def apply(self, current: KnowledgeEntry, candidates: Sequence[KnowledgeEntry]) -> KnowledgeEntry:
        """
        Applies a specific aggregation concern (e.g., confidence evolution, evidence accumulation)
        to the current knowledge entry, based on the full set of candidates.
        
        Args:
            current: The aggregated knowledge entry being built. Must remain immutable.
            candidates: The original set of identical candidate observations.
            
        Returns:
            KnowledgeEntry: A new immutable knowledge entry with the rule applied.
        """
        pass


class IKnowledgeAggregationEngine(ABC):
    """
    Orchestrates the transformation of candidate knowledge assertions into
    durable organizational knowledge.
    """
    
    @abstractmethod
    async def aggregate_candidate_knowledge(self) -> Sequence[KnowledgeEntry]:
        """
        Retrieves candidate knowledge, groups identical observations, applies aggregation rules,
        and produces aggregated knowledge.
        
        Returns:
            Sequence[KnowledgeEntry]: The aggregated durable organizational knowledge.
        """
        pass
