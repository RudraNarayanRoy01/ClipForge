from typing import Sequence

from src.reasoning.knowledge.models import KnowledgeEntry
from src.reasoning.knowledge.repository.interfaces import IKnowledgeRepository
from src.reasoning.knowledge.query.interfaces import (
    IKnowledgeQueryEngine,
    KnowledgeQuery,
    IKnowledgeFilter,
    IQueryPolicy
)


class DefaultKnowledgeQueryEngine(IKnowledgeQueryEngine):
    """
    Orchestrates deterministic retrieval of organizational knowledge.
    
    Composed of an injected sequence of filters and a query policy, ensuring the engine
    remains closed for modification while allowing future filters and policies.
    """
    
    def __init__(
        self,
        repository: IKnowledgeRepository,
        filters: Sequence[IKnowledgeFilter],
        policy: IQueryPolicy
    ):
        self._repository = repository
        self._filters = filters
        self._policy = policy

    async def query(self, query: KnowledgeQuery) -> Sequence[KnowledgeEntry]:
        """
        Executes the retrieval workflow:
        1. Retrieves organizational knowledge from passive persistence.
        2. Applies all injected filters in sequence.
        3. Applies the execution policy (deterministic ordering, etc.).
        """
        # 1. Retrieve all accumulated organizational knowledge
        # The repository is treated purely as a passive persistence boundary
        entries = await self._repository.retrieve_accumulated_knowledge()
        
        # 2. Apply filters sequentially
        for knowledge_filter in self._filters:
            entries = knowledge_filter.apply(query, entries)
            
        # 3. Apply execution policy (deterministic ordering, limits)
        return self._policy.apply_policy(entries)
