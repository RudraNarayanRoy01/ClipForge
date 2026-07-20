from typing import Sequence

from src.reasoning.knowledge.models import KnowledgeEntry
from src.reasoning.knowledge.query.interfaces import IKnowledgeFilter, KnowledgeQuery


class CategoryFilter(IKnowledgeFilter):
    """Filters knowledge entries by category."""
    
    def apply(self, query: KnowledgeQuery, entries: Sequence[KnowledgeEntry]) -> Sequence[KnowledgeEntry]:
        if query.category is None:
            return entries
            
        return [e for e in entries if e.category == query.category]


class SubjectFilter(IKnowledgeFilter):
    """Filters knowledge entries by exact, case-insensitive subject match."""
    
    def apply(self, query: KnowledgeQuery, entries: Sequence[KnowledgeEntry]) -> Sequence[KnowledgeEntry]:
        if query.subject is None:
            return entries
            
        subject_lower = query.subject.lower()
        return [e for e in entries if e.subject.lower() == subject_lower]


class SourceFilter(IKnowledgeFilter):
    """Filters knowledge entries by origination source."""
    
    def apply(self, query: KnowledgeQuery, entries: Sequence[KnowledgeEntry]) -> Sequence[KnowledgeEntry]:
        if query.source is None:
            return entries
            
        return [
            e for e in entries 
            if any(ev.source == query.source for ev in e.evidence)
        ]


class ConfidenceFilter(IKnowledgeFilter):
    """Filters knowledge entries by confidence level."""
    
    def apply(self, query: KnowledgeQuery, entries: Sequence[KnowledgeEntry]) -> Sequence[KnowledgeEntry]:
        if query.confidence is None:
            return entries
            
        return [e for e in entries if e.confidence == query.confidence]
