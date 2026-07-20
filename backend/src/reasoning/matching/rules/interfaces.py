from dataclasses import dataclass, field
from typing import List, Optional
from abc import ABC, abstractmethod

from src.domain.campaign_entities import Campaign
from src.reasoning.knowledge.models import KnowledgeEntry
from src.reasoning.matching.models import MatchConfidence, MatchRequest


@dataclass(frozen=True)
class MatchingContext:
    """
    Immutable context that encapsulates the information required for a rule evaluation.
    Composed of domain objects to preserve encapsulation and avoid parameter explosion.
    """
    campaign: Campaign
    knowledge: List[KnowledgeEntry]
    request: MatchRequest


@dataclass(frozen=True)
class RuleEvaluationResult:
    """
    Structured result of a rule evaluation.
    Captures the decision, evidence, and explanation deterministically.
    """
    is_matched: bool
    evidence: List[str] = field(default_factory=list)
    explanation: str = ""
    confidence: Optional[MatchConfidence] = None


class IMatchingRule(ABC):
    """
    Interface for a deterministic matching rule.
    Each rule owns one responsibility and does not perform orchestration.
    """

    @abstractmethod
    def evaluate(self, context: MatchingContext) -> RuleEvaluationResult:
        """
        Evaluates the rule against the provided domain context.

        Args:
            context (MatchingContext): The immutable domain state.

        Returns:
            RuleEvaluationResult: The deterministic evaluation outcome.
        """
        pass
