from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Protocol, Tuple

from src.application.execution_models import RenderExecutionRequest


class PolicyViolationSeverity(Enum):
    """
    Severity of a policy violation.
    BLOCKER: Execution must be prevented.
    WARNING: Execution is allowed, but warnings should be logged or returned.
    """
    WARNING = auto()
    BLOCKER = auto()


class RenderExecutionDecision(Enum):
    """
    Final decision of the policy evaluation.
    """
    ALLOW = auto()
    ALLOW_WITH_WARNINGS = auto()
    DENY = auto()


@dataclass(frozen=True)
class PolicyViolation:
    """
    An immutable record of a policy constraint violation.
    """
    code: str
    description: str
    severity: PolicyViolationSeverity


@dataclass(frozen=True)
class RenderExecutionPolicyResult:
    """
    The immutable final result of policy evaluation.
    """
    decision: RenderExecutionDecision
    violations: tuple[PolicyViolation, ...] = field(default_factory=tuple)

    @classmethod
    def allow(cls) -> "RenderExecutionPolicyResult":
        return cls(decision=RenderExecutionDecision.ALLOW)

    @classmethod
    def deny(cls, violations: List[PolicyViolation]) -> "RenderExecutionPolicyResult":
        return cls(
            decision=RenderExecutionDecision.DENY,
            violations=tuple(violations)
        )

    @classmethod
    def allow_with_warnings(cls, violations: List[PolicyViolation]) -> "RenderExecutionPolicyResult":
        return cls(
            decision=RenderExecutionDecision.ALLOW_WITH_WARNINGS,
            violations=tuple(violations)
        )


class RenderExecutionPolicyRule(Protocol):
    """
    Protocol for a stateless, purely functional policy rule.
    """
    
    @property
    def name(self) -> str:
        """
        A unique name for the rule, used to ensure deterministic evaluation order.
        """
        ...

    def evaluate(self, request: RenderExecutionRequest) -> List[PolicyViolation]:
        """
        Evaluate the execution request and return a list of violations.
        Must not mutate the request, lifecycle, or communicate with infrastructure.
        """
        ...


class RenderExecutionPolicy:
    """
    Evaluates a RenderExecutionRequest against a set of rules.
    It is deterministic, stateless, and collects all violations (including warnings
    and blockers) without failing fast.
    """
    def __init__(self, rules: List[RenderExecutionPolicyRule]):
        # Sort rules by name for deterministic evaluation order
        self._rules = sorted(rules, key=lambda rule: rule.name)

    def evaluate(self, request: RenderExecutionRequest) -> RenderExecutionPolicyResult:
        """
        Evaluates the request across all registered rules.
        """
        all_violations: List[PolicyViolation] = []
        
        for rule in self._rules:
            violations = rule.evaluate(request)
            if violations:
                all_violations.extend(violations)

        has_blockers = any(v.severity == PolicyViolationSeverity.BLOCKER for v in all_violations)
        has_warnings = any(v.severity == PolicyViolationSeverity.WARNING for v in all_violations)

        if has_blockers:
            return RenderExecutionPolicyResult.deny(all_violations)
        elif has_warnings:
            return RenderExecutionPolicyResult.allow_with_warnings(all_violations)
        
        return RenderExecutionPolicyResult.allow()
