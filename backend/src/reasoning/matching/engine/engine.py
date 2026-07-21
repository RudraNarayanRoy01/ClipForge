import uuid
from typing import List

from src.reasoning.matching.engine.interfaces import IMatchingEngine
from src.reasoning.matching.exceptions import EngineExecutionError
from src.reasoning.matching.models import (
    MatchedRequirement,
    MatchResult,
)
from src.reasoning.matching.rules.interfaces import (
    IMatchingRule,
    MatchingContext,
    RuleEvaluationResult,
)


class DefaultMatchingEngine(IMatchingEngine):
    """
    Default implementation of IMatchingEngine.
    Coordinates rule execution without embedding any business policy.
    """

    def __init__(self, rules: List[IMatchingRule]):
        """
        Initializes the engine with a set of matching rules.
        Dependency Injection: Engine depends only on abstractions.
        """
        self._rules = list(rules)

    def evaluate(self, context: MatchingContext) -> MatchResult:
        """
        Executes each injected rule independently and sequentially.
        Assembles a MatchResult from the RuleEvaluationResults.
        """
        is_successful = True
        matched_requirements: List[MatchedRequirement] = []
        all_evidence: List[str] = []

        for rule in self._rules:
            try:
                # Rule execution is independent
                result: RuleEvaluationResult = rule.evaluate(context)
                
                # We collect every evaluation result
                requirement = MatchedRequirement(
                    requirement_id=uuid.uuid4(),
                    description=result.explanation or type(rule).__name__,
                    is_met=result.is_matched,
                    confidence=result.confidence,
                )
                matched_requirements.append(requirement)
                
                if result.evidence:
                    all_evidence.extend(result.evidence)
                
                if not result.is_matched:
                    is_successful = False

            except Exception as e:
                # Exception chaining: wrap lower-level exceptions
                raise EngineExecutionError(
                    f"Rule {type(rule).__name__} failed during evaluation"
                ) from e

        # Assemble MatchResult
        # We defer confidence determination to the Match Policy.
        
        # We include all gathered evidence in reasoning
        reasoning = "Engine evaluation completed deterministically."
        if all_evidence:
            reasoning += " Evidence: " + " | ".join(all_evidence)

        return MatchResult(
            request_id=context.request.id,
            is_successful=is_successful,
            confidence=None,
            matched_requirements=matched_requirements,
            knowledge_matches=[],
            reasoning=reasoning,
        )

