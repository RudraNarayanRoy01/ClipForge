from typing import List

from src.reasoning.extraction.models import CampaignEntityDocument
from .interfaces import IEligibilityRule
from .models import EligibilityIssue, IssueSeverity


class CompletenessRule(IEligibilityRule):
    """
    Checks if the campaign contains basic actionable information.
    A campaign must have at least some requirements or deliverables to be actionable.
    """
    
    def evaluate(self, document: CampaignEntityDocument) -> List[EligibilityIssue]:
        issues = []
        
        has_requirements = len(document.requirements) > 0
        has_deliverables = len(document.deliverables) > 0
        
        if not has_requirements and not has_deliverables:
            issues.append(
                EligibilityIssue(
                    rule_name=self.__class__.__name__,
                    severity=IssueSeverity.ERROR,
                    description="Campaign lacks both requirements and deliverables, making it unactionable."
                )
            )
            
        return issues


class PlatformRecognitionRule(IEligibilityRule):
    """
    Checks if at least one target platform is recognized for the campaign.
    """
    
    def evaluate(self, document: CampaignEntityDocument) -> List[EligibilityIssue]:
        issues = []
        
        if len(document.platforms) == 0:
            issues.append(
                EligibilityIssue(
                    rule_name=self.__class__.__name__,
                    severity=IssueSeverity.ERROR,
                    description="No recognizable target platforms were identified for this campaign."
                )
            )
            
        return issues


class RequiredInformationRule(IEligibilityRule):
    """
    Checks for the presence of required informational entities like rewards.
    """
    
    def evaluate(self, document: CampaignEntityDocument) -> List[EligibilityIssue]:
        issues = []
        
        if len(document.rewards) == 0:
            issues.append(
                EligibilityIssue(
                    rule_name=self.__class__.__name__,
                    severity=IssueSeverity.WARNING,
                    description="No rewards or payouts are listed. The campaign might be unpaid or require manual review."
                )
            )
            
        return issues


class ConsistencyRule(IEligibilityRule):
    """
    Checks for obvious logical flaws in the parsed entities.
    For instance, having restrictions but completely lacking actionable deliverables.
    """
    
    def evaluate(self, document: CampaignEntityDocument) -> List[EligibilityIssue]:
        issues = []
        
        has_restrictions = len(document.restrictions) > 0
        has_actionable = len(document.deliverables) > 0 or len(document.requirements) > 0
        
        if has_restrictions and not has_actionable:
            issues.append(
                EligibilityIssue(
                    rule_name=self.__class__.__name__,
                    severity=IssueSeverity.WARNING,
                    description="Campaign has restrictions but no actionable deliverables or requirements."
                )
            )
            
        return issues
