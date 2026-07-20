from abc import ABC, abstractmethod
import uuid
from typing import Sequence

from src.reasoning.knowledge.models import KnowledgeEntry
from src.reasoning.knowledge.query.interfaces import KnowledgeQuery

class IKnowledgeService(ABC):
    """
    Public entry point for the Campaign Knowledge subsystem.
    Composes Repository, Aggregation, and Query capabilities into a single cohesive API.
    
    This service should be used by all external consumers to interact with organizational knowledge.
    It exposes business-oriented operations rather than implementation details.
    """

    @abstractmethod
    async def ingest_candidate_knowledge(self, entry: KnowledgeEntry) -> None:
        """
        Ingests a new candidate knowledge observation into the system.
        This knowledge is considered 'candidate' until it undergoes aggregation.
        
        Args:
            entry: The candidate knowledge observation.
        """
        pass

    @abstractmethod
    async def refresh_organizational_knowledge(self) -> Sequence[KnowledgeEntry]:
        """
        Coordinates the aggregation of all candidate knowledge into durable organizational knowledge.
        This consolidates observations, resolves duplicates, and evolves confidence.
        
        Returns:
            Sequence[KnowledgeEntry]: The resulting aggregated knowledge.
        """
        pass

    @abstractmethod
    async def query_knowledge(self, query: KnowledgeQuery) -> Sequence[KnowledgeEntry]:
        """
        Executes a deterministic retrieval query against accumulated knowledge.
        
        Args:
            query: The business criteria to search by.
            
        Returns:
            Sequence[KnowledgeEntry]: The knowledge entries matching the criteria.
        """
        pass

    @abstractmethod
    async def get_knowledge(self, knowledge_id: uuid.UUID) -> KnowledgeEntry:
        """
        Retrieves a specific knowledge entry by its unique identifier.
        
        Args:
            knowledge_id: The UUID of the knowledge entry.
            
        Returns:
            KnowledgeEntry: The requested knowledge entry.
        """
        pass
