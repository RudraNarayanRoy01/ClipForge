from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Sequence

from src.reasoning.knowledge.models import (
    KnowledgeEntry,
    KnowledgeCategory,
    KnowledgeSource,
    KnowledgeConfidence
)


@dataclass(frozen=True)
class KnowledgeQuery:
    """
    Represents deterministic business retrieval criteria for organizational knowledge.
    Immutable to prevent modification during execution.
    """
    category: Optional[KnowledgeCategory] = None
    subject: Optional[str] = None
    source: Optional[KnowledgeSource] = None
    confidence: Optional[KnowledgeConfidence] = None


class IQueryPolicy(ABC):
    """
    Abstraction responsible for query execution behavior.
    Handles deterministic ordering and future execution logic like limits.
    Separates execution policies from filtering logic.
    """
    @abstractmethod
    def apply_policy(self, entries: Sequence[KnowledgeEntry]) -> Sequence[KnowledgeEntry]:
        """Applies execution policies such as sorting to the final result set."""
        pass


class IKnowledgeFilter(ABC):
    """
    Independent filter component that addresses one retrieval concern.
    """
    @abstractmethod
    def apply(self, query: KnowledgeQuery, entries: Sequence[KnowledgeEntry]) -> Sequence[KnowledgeEntry]:
        """
        Applies the filter to the provided knowledge entries based on the query.
        If the filter criteria are not specified in the query, it returns the entries unmodified.
        """
        pass


class IKnowledgeQueryEngine(ABC):
    """
    Orchestrates deterministic retrieval of organizational knowledge.
    Applies filters and execution policies without performing aggregation or modifying knowledge.
    """
    @abstractmethod
    async def query(self, query: KnowledgeQuery) -> Sequence[KnowledgeEntry]:
        """
        Executes a deterministic retrieval query.
        """
        pass
