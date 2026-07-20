from typing import Sequence

from src.reasoning.knowledge.models import KnowledgeEntry
from src.reasoning.knowledge.query.interfaces import IQueryPolicy


class DefaultQueryPolicy(IQueryPolicy):
    """
    Default policy that enforces strict deterministic ordering.
    """
    
    def apply_policy(self, entries: Sequence[KnowledgeEntry]) -> Sequence[KnowledgeEntry]:
        """
        Orders knowledge deterministically by category, subject, confidence, and ID.
        """
        return sorted(
            entries,
            key=lambda e: (
                e.category.name,
                e.subject,
                e.confidence.name,
                str(e.id)
            )
        )
