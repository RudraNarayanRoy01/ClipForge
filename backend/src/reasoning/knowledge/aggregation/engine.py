from typing import Sequence, List, Dict, Tuple
from dataclasses import replace
import uuid

from src.reasoning.knowledge.models import KnowledgeEntry, KnowledgeSource, KnowledgeCategory
from src.reasoning.knowledge.repository.interfaces import IKnowledgeRepository
from .interfaces import IKnowledgeAggregationEngine, IKnowledgeAggregationRule


class DefaultKnowledgeAggregationEngine(IKnowledgeAggregationEngine):
    """
    Default deterministic implementation of the Knowledge Aggregation Engine.
    Retrieves candidate knowledge from the repository, groups identical observations,
    and applies independent aggregation rules.
    """
    
    def __init__(self, repository: IKnowledgeRepository, rules: Sequence[IKnowledgeAggregationRule]):
        self._repository = repository
        self._rules = rules
        
    async def aggregate_candidate_knowledge(self) -> Sequence[KnowledgeEntry]:
        """
        Retrieves candidate knowledge, groups identical observations, applies aggregation rules,
        and produces aggregated knowledge.
        """
        
        # 1. Retrieve all candidate knowledge assertions
        candidates = await self._repository.retrieve_knowledge_by_source(KnowledgeSource.CAMPAIGN_EVALUATION)
        
        if not candidates:
            return []
            
        # 2. Group identical observations
        # The key is a tuple of (category, subject, value) which naturally preserves conflicts.
        # Conflicting values for the same subject will hash to different groups.
        groups: Dict[Tuple[KnowledgeCategory, str, str], List[KnowledgeEntry]] = {}
        
        for candidate in candidates:
            key = (candidate.category, candidate.subject, candidate.value)
            if key not in groups:
                groups[key] = []
            groups[key].append(candidate)
            
        # 3. Apply aggregation rules to each group
        aggregated_entries: List[KnowledgeEntry] = []
        
        for (category, subject, value), group_candidates in groups.items():
            # Create a base aggregated entry representing this distinct observation.
            # We use a new UUID because this is a new durable entity representing the aggregation.
            # We seed it with the first candidate's confidence, but rules will evolve it.
            base_entry = KnowledgeEntry(
                id=uuid.uuid4(),
                category=category,
                subject=subject,
                value=value,
                confidence=group_candidates[0].confidence,
                evidence=[], # Evidence will be populated by EvidenceAggregationRule
                created_at=group_candidates[0].created_at # Or we could use datetime.now(timezone.utc)
            )
            
            # Pass the base entry through all configured rules
            current_entry = base_entry
            for rule in self._rules:
                current_entry = rule.apply(current_entry, group_candidates)
                
            aggregated_entries.append(current_entry)
            
        return aggregated_entries
