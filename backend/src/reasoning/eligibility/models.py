from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List


class EligibilityStatus(Enum):
    """
    Represents the final decision on whether a campaign is eligible for processing.
    """
    ELIGIBLE = auto()
    INELIGIBLE = auto()
    NEEDS_REVIEW = auto()


class IssueSeverity(Enum):
    """
    Severity of a found eligibility issue.
    """
    WARNING = auto()
    ERROR = auto()


@dataclass(frozen=True)
class EligibilityIssue:
    """
    An immutable record of a specific eligibility concern found by a rule.
    """
    rule_name: str
    severity: IssueSeverity
    description: str


@dataclass(frozen=True)
class EligibilityAssessment:
    """
    The immutable result of the Eligibility Assessment Engine.
    """
    status: EligibilityStatus
    issues: List[EligibilityIssue] = field(default_factory=list)

    @property
    def is_eligible(self) -> bool:
        return self.status == EligibilityStatus.ELIGIBLE
