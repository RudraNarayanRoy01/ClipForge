from .models import (
    WorthItRating,
    AssessmentConfidence,
    WorthItFinding,
    WorthItAssessment,
)
from .interfaces import (
    IWorthItRule,
    IWorthItAssessmentEngine,
)
from .rules import (
    RewardRule,
    DeliverableRule,
    DeadlineRule,
    ComplexityRule,
    CompletenessRule,
)
from .engine import DefaultWorthItAssessmentEngine

def create_worth_it_engine() -> IWorthItAssessmentEngine:
    """
    Factory function to create the standard Worth-It Assessment Engine 
    with the default set of deterministic rules.
    """
    rules = [
        RewardRule(),
        DeliverableRule(),
        DeadlineRule(),
        ComplexityRule(),
        CompletenessRule(),
    ]
    return DefaultWorthItAssessmentEngine(rules=rules)

__all__ = [
    "WorthItRating",
    "AssessmentConfidence",
    "WorthItFinding",
    "WorthItAssessment",
    "IWorthItRule",
    "IWorthItAssessmentEngine",
    "create_worth_it_engine",
]
