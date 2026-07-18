from typing import List

from src.reasoning.extraction.models import CampaignEntityDocument
from src.reasoning.eligibility.models import EligibilityAssessment
from .interfaces import IWorthItRule
from .models import WorthItFinding


class RewardRule(IWorthItRule):
    """
    Observes the presence and volume of rewards in the campaign.
    """
    
    def evaluate(
        self, 
        document: CampaignEntityDocument, 
        eligibility: EligibilityAssessment
    ) -> List[WorthItFinding]:
        findings = []
        
        if len(document.rewards) > 0:
            findings.append(
                WorthItFinding(
                    rule_name=self.__class__.__name__,
                    observation="Reward Present",
                    description=f"Campaign explicitly lists {len(document.rewards)} reward(s)."
                )
            )
        else:
            findings.append(
                WorthItFinding(
                    rule_name=self.__class__.__name__,
                    observation="Reward Missing",
                    description="No explicit rewards are listed for this campaign."
                )
            )
            
        return findings


class DeliverableRule(IWorthItRule):
    """
    Observes the volume of expected deliverables.
    """
    
    def evaluate(
        self, 
        document: CampaignEntityDocument, 
        eligibility: EligibilityAssessment
    ) -> List[WorthItFinding]:
        findings = []
        
        count = len(document.deliverables)
        if count == 0:
            findings.append(
                WorthItFinding(
                    rule_name=self.__class__.__name__,
                    observation="Deliverable Missing",
                    description="No specific deliverables are requested."
                )
            )
        elif count > 3:
            findings.append(
                WorthItFinding(
                    rule_name=self.__class__.__name__,
                    observation="High Deliverable Count",
                    description=f"Campaign requests {count} deliverables, which is a high workload."
                )
            )
        else:
            findings.append(
                WorthItFinding(
                    rule_name=self.__class__.__name__,
                    observation="Standard Deliverable Count",
                    description=f"Campaign requests {count} deliverable(s)."
                )
            )
            
        return findings


class DeadlineRule(IWorthItRule):
    """
    Observes the presence of deadlines.
    """
    
    def evaluate(
        self, 
        document: CampaignEntityDocument, 
        eligibility: EligibilityAssessment
    ) -> List[WorthItFinding]:
        findings = []
        
        if len(document.deadlines) > 0:
            findings.append(
                WorthItFinding(
                    rule_name=self.__class__.__name__,
                    observation="Deadline Present",
                    description=f"Campaign lists {len(document.deadlines)} deadline(s)."
                )
            )
        else:
            findings.append(
                WorthItFinding(
                    rule_name=self.__class__.__name__,
                    observation="Deadline Missing",
                    description="No deadlines are explicitly stated."
                )
            )
            
        return findings


class ComplexityRule(IWorthItRule):
    """
    Observes operational complexity based on restrictions, requirements, and audio rules.
    """
    
    def evaluate(
        self, 
        document: CampaignEntityDocument, 
        eligibility: EligibilityAssessment
    ) -> List[WorthItFinding]:
        findings = []
        
        complexity_factors = len(document.restrictions) + len(document.requirements) + len(document.audio_rules)
        
        if complexity_factors > 5:
            findings.append(
                WorthItFinding(
                    rule_name=self.__class__.__name__,
                    observation="High Complexity",
                    description=f"Campaign has {complexity_factors} constraints (restrictions, requirements, audio rules)."
                )
            )
        elif complexity_factors > 0:
            findings.append(
                WorthItFinding(
                    rule_name=self.__class__.__name__,
                    observation="Standard Complexity",
                    description=f"Campaign has {complexity_factors} constraints."
                )
            )
        else:
            findings.append(
                WorthItFinding(
                    rule_name=self.__class__.__name__,
                    observation="Low Complexity",
                    description="Campaign has no specific constraints."
                )
            )
            
        return findings


class CompletenessRule(IWorthItRule):
    """
    Observes missing critical information which might reduce confidence in the assessment.
    """
    
    def evaluate(
        self, 
        document: CampaignEntityDocument, 
        eligibility: EligibilityAssessment
    ) -> List[WorthItFinding]:
        findings = []
        
        if len(document.rewards) == 0:
            findings.append(
                WorthItFinding(
                    rule_name=self.__class__.__name__,
                    observation="Missing Reward Information",
                    description="Lack of explicit reward makes economic assessment difficult.",
                    is_missing_information=True
                )
            )
            
        if len(document.deliverables) == 0 and len(document.requirements) == 0:
            findings.append(
                WorthItFinding(
                    rule_name=self.__class__.__name__,
                    observation="Missing Actionable Information",
                    description="Lack of clear deliverables or requirements makes workload assessment difficult.",
                    is_missing_information=True
                )
            )
            
        return findings
