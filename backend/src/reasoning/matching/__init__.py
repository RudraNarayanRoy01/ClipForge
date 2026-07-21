"""
Campaign Matching Domain

This package establishes the immutable domain language and models for
campaign matching. It provides the vocabulary for evaluating requirements,
knowledge, and constraints without implementing the underlying algorithms
or persistence mechanisms.
"""

from .models import (
    MatchRequest,
    MatchResult,
    KnowledgeMatch,
    MatchedRequirement,
    MatchingScope,
    MatchingConstraints,
    MatchConfidence,
    PolicyDecision,
    PolicyRationale,
)

from .exceptions import (
    MatchingException,
    InvalidMatchRequest,
    InvalidMatchingScope,
    EngineExecutionError,
    MatchingServiceError,
)

__all__ = [
    "MatchRequest",
    "MatchResult",
    "KnowledgeMatch",
    "MatchedRequirement",
    "MatchingScope",
    "MatchingConstraints",
    "MatchConfidence",
    "PolicyDecision",
    "PolicyRationale",
    "MatchingException",
    "InvalidMatchRequest",
    "InvalidMatchingScope",
    "EngineExecutionError",
    "MatchingServiceError",
]
