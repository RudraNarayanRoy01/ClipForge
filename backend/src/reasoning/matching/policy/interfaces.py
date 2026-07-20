from abc import ABC, abstractmethod
from src.reasoning.matching.models import MatchResult, PolicyDecision

class IMatchPolicy(ABC):
    """
    Interface for interpreting MatchResults and producing consistent business decisions.
    The policy separates business interpretation from rule execution and orchestration.
    """
    
    @abstractmethod
    def evaluate(self, result: MatchResult) -> PolicyDecision:
        """
        Evaluates a MatchResult and determines the business outcome.
        
        Args:
            result (MatchResult): The immutable outcome of a matching process.
            
        Returns:
            PolicyDecision: An immutable domain object representing business conclusions.
        """
        pass
