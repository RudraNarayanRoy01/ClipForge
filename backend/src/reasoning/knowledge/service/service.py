import uuid
from typing import Sequence

from src.reasoning.knowledge.models import KnowledgeEntry
from src.reasoning.knowledge.repository.interfaces import IKnowledgeRepository
from src.reasoning.knowledge.aggregation.interfaces import IKnowledgeAggregationEngine
from src.reasoning.knowledge.query.interfaces import IKnowledgeQueryEngine, KnowledgeQuery
from src.reasoning.knowledge.service.interfaces import IKnowledgeService

class DefaultKnowledgeService(IKnowledgeService):
    """
    Default implementation of the Campaign Knowledge subsystem entry point.
    Strictly coordinates existing components without duplicating their business logic.
    """

    def __init__(
        self,
        repository: IKnowledgeRepository,
        aggregation_engine: IKnowledgeAggregationEngine,
        query_engine: IKnowledgeQueryEngine
    ):
        self._repository = repository
        self._aggregation_engine = aggregation_engine
        self._query_engine = query_engine

    async def ingest_candidate_knowledge(self, entry: KnowledgeEntry) -> None:
        """
        Delegates candidate storage to the repository.
        """
        await self._repository.store_candidate_knowledge(entry)

    async def refresh_organizational_knowledge(self) -> Sequence[KnowledgeEntry]:
        """
        Coordinates the aggregation of candidate knowledge.
        Delegates the logic to the aggregation engine.
        """
        return await self._aggregation_engine.aggregate_candidate_knowledge()

    async def query_knowledge(self, query: KnowledgeQuery) -> Sequence[KnowledgeEntry]:
        """
        Delegates retrieval queries to the query engine.
        """
        return await self._query_engine.query(query)

    async def get_knowledge(self, knowledge_id: uuid.UUID) -> KnowledgeEntry:
        """
        Delegates point lookups to the repository.
        """
        return await self._repository.retrieve_knowledge_by_id(knowledge_id)
