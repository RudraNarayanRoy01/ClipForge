from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List


class WorthItRating(Enum):
    """Overall economic and operational rating of the campaign."""
    EXCELLENT = auto()
    GOOD = auto()
    FAIR = auto()
    POOR = auto()
    UNKNOWN = auto()


class AssessmentConfidence(Enum):
    """Confidence in the assessment based on available information."""
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()


@dataclass(frozen=True)
class WorthItFinding:
    """
    An objective observation made by a worth-it rule.
    """
    rule_name: str
    observation: str
    description: str
    is_missing_information: bool = False


@dataclass(frozen=True)
class WorthItAssessment:
    """
    The immutable result of the Worth-It Assessment Engine.
    Contains the overall rating, confidence, and objective findings.
    """
    overall_rating: WorthItRating
    confidence: AssessmentConfidence
    findings: List[WorthItFinding] = field(default_factory=list)
