from abc import ABC, abstractmethod
import uuid
from typing import Sequence

from src.reasoning.knowledge.models import (
    KnowledgeEntry,
    KnowledgeCategory,
    KnowledgeSource
)

class IKnowledgeRepository(ABC):
    """
    Interface for the Campaign Knowledge repository.
    Defines the persistence contracts for the reasoning domain without coupling
    to any underlying storage mechanics or infrastructure implementations.

    IMPORTANT: This repository serves strictly as a persistence boundary.
    It manages distinct stages of the knowledge lifecycle (candidate vs. accumulated)
    but does NOT perform aggregation logic. Responsibilities such as confidence 
    evolution, duplicate resolution, conflict resolution, and the promotion of 
    candidate knowledge belong exclusively to the aggregation subsystem (future batch).
    """

    @abstractmethod
    async def store_candidate_knowledge(self, entry: KnowledgeEntry) -> None:
        """
        Persists observations produced by Knowledge Extraction.
        
        These are candidate knowledge assertions that have not yet undergone
        aggregation, duplicate resolution, or confidence evolution.
        
        Args:
            entry: The candidate knowledge entry to store.
        """
        pass

    @abstractmethod
    async def retrieve_accumulated_knowledge(self) -> Sequence[KnowledgeEntry]:
        """
        Retrieves organizational knowledge that has already passed through future aggregation.
        
        This represents the unified, evolved, and deduplicated knowledge state 
        resulting from the aggregation process.
        
        Returns:
            Sequence[KnowledgeEntry]: A collection of all durable, accumulated knowledge entries.
        """
        pass

    @abstractmethod
    async def retrieve_knowledge_by_category(self, category: KnowledgeCategory) -> Sequence[KnowledgeEntry]:
        """
        Retrieves knowledge assertions specific to a given category.
        
        Args:
            category: The domain category to filter by.
            
        Returns:
            Sequence[KnowledgeEntry]: The knowledge entries belonging to the category.
        """
        pass

    @abstractmethod
    async def retrieve_knowledge_by_source(self, source: KnowledgeSource) -> Sequence[KnowledgeEntry]:
        """
        Retrieves knowledge assertions that originated from a specific source.
        
        Args:
            source: The origination source to filter by.
            
        Returns:
            Sequence[KnowledgeEntry]: The knowledge entries from the specified source.
        """
        pass
        
    @abstractmethod
    async def retrieve_knowledge_by_id(self, knowledge_id: uuid.UUID) -> KnowledgeEntry:
        """
        Retrieves a specific knowledge entry by its unique identifier.
        
        Args:
            knowledge_id: The UUID of the knowledge entry.
            
        Returns:
            KnowledgeEntry: The requested knowledge entry.
            
        Raises:
            ValueError: If the knowledge entry cannot be found.
        """
        pass
