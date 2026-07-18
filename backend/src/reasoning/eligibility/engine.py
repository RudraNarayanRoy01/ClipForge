from typing import Sequence

from src.reasoning.extraction.models import CampaignEntityDocument
from .interfaces import IEligibilityAssessmentEngine, IEligibilityRule
from .models import EligibilityAssessment, EligibilityIssue, EligibilityStatus, IssueSeverity


class DefaultEligibilityAssessmentEngine(IEligibilityAssessmentEngine):
    """
    Default implementation of the Eligibility Assessment Engine.
    Evaluates a document against a configured sequence of rules and aggregates the results deterministically.
    """
    
    def __init__(self, rules: Sequence[IEligibilityRule]):
        self._rules = rules
        
    def assess(self, document: CampaignEntityDocument) -> EligibilityAssessment:
        all_issues = []
        
        for rule in self._rules:
            issues = rule.evaluate(document)
            all_issues.extend(issues)
            
        status = self._determine_status(all_issues)
        
        return EligibilityAssessment(
            status=status,
            issues=all_issues
        )
        
    def _determine_status(self, issues: list[EligibilityIssue]) -> EligibilityStatus:
        if any(issue.severity == IssueSeverity.ERROR for issue in issues):
            return EligibilityStatus.INELIGIBLE
            
        if any(issue.severity == IssueSeverity.WARNING for issue in issues):
            return EligibilityStatus.NEEDS_REVIEW
            
        return EligibilityStatus.ELIGIBLE
