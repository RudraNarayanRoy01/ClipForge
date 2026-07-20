import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional


class MatchConfidence(Enum):
    """
    Represents the confidence level of a match.
    Provides deterministic categorization instead of float bounds where possible.
    """
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()


class MatchingScope(Enum):
    """
    Defines the boundaries or strictness of the matching evaluation.
    """
    STRICT = auto()
    RELAXED = auto()
    BROAD = auto()


@dataclass(frozen=True)
class MatchingConstraints:
    """
    Immutable parameters defining how strict the match must be.
    """
    require_all_mandatory: bool = True
    minimum_confidence: MatchConfidence = MatchConfidence.MEDIUM


@dataclass(frozen=True)
class MatchRequest:
    """
    Represents an immutable request to perform a matching evaluation.
    This acts as the input vector to the matching domain without describing how to match.
    """
    target_id: uuid.UUID
    scope: MatchingScope
    constraints: MatchingConstraints = field(default_factory=MatchingConstraints)
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class MatchedRequirement:
    """
    Represents the evaluation of a specific, atomic requirement within a match.
    """
    requirement_id: uuid.UUID
    description: str
    is_met: bool


@dataclass(frozen=True)
class KnowledgeMatch:
    """
    Represents a piece of domain knowledge that was applied or matched during evaluation.
    Each match decision has its own unique identity for future referencing (e.g. auditing, explanations).
    """
    knowledge_id: uuid.UUID
    relevance_score: float  # Value between 0.0 and 1.0 representing mathematical relevance
    description: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class MatchResult:
    """
    Represents the immutable outcome of a matching process.
    Provides full explainability for why a match succeeded or failed.
    """
    request_id: uuid.UUID
    is_successful: bool
    confidence: MatchConfidence
    matched_requirements: List[MatchedRequirement] = field(default_factory=list)
    knowledge_matches: List[KnowledgeMatch] = field(default_factory=list)
    reasoning: Optional[str] = None
