from .engine import DefaultEligibilityAssessmentEngine
from .interfaces import IEligibilityAssessmentEngine, IEligibilityRule
from .models import EligibilityAssessment, EligibilityIssue, EligibilityStatus, IssueSeverity
from .rules import CompletenessRule, ConsistencyRule, PlatformRecognitionRule, RequiredInformationRule

def create_eligibility_engine() -> IEligibilityAssessmentEngine:
    """
    Factory function to create the standard Eligibility Assessment Engine 
    with the default set of deterministic rules.
    """
    rules = [
        CompletenessRule(),
        PlatformRecognitionRule(),
        RequiredInformationRule(),
        ConsistencyRule(),
    ]
    return DefaultEligibilityAssessmentEngine(rules=rules)

__all__ = [
    "IEligibilityAssessmentEngine",
    "IEligibilityRule",
    "EligibilityAssessment",
    "EligibilityIssue",
    "EligibilityStatus",
    "IssueSeverity",
    "create_eligibility_engine",
]
