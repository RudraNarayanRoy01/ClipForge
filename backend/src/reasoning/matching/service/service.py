from typing import List

from src.domain.campaign_entities import Campaign
from src.reasoning.knowledge.models import KnowledgeEntry
from src.reasoning.matching.engine.interfaces import IMatchingEngine
from src.reasoning.matching.exceptions import MatchingException, MatchingServiceError
from src.reasoning.matching.models import MatchingOutcome, MatchRequest
from src.reasoning.matching.policy.interfaces import IMatchPolicy
from src.reasoning.matching.rules.interfaces import MatchingContext
from src.reasoning.matching.service.interfaces import IMatchingContextFactory, IMatchingService


class DefaultMatchingContextFactory(IMatchingContextFactory):
    """
    Default factory for constructing the MatchingContext.
    Transforms application inputs into the domain state required by the engine.
    """
    
    def create(
        self, 
        request: MatchRequest, 
        campaign: Campaign, 
        knowledge: List[KnowledgeEntry]
    ) -> MatchingContext:
        """
        Constructs the immutable MatchingContext.
        """
        if not request:
            raise ValueError("MatchRequest cannot be None.")
        if not campaign:
            raise ValueError("Campaign cannot be None.")
        if knowledge is None:
            raise ValueError("Knowledge list cannot be None.")
            
        return MatchingContext(
            campaign=campaign,
            knowledge=knowledge,
            request=request
        )


class DefaultMatchingService(IMatchingService):
    """
    Default implementation of the Matching Service.
    Orchestrates the matching workflow by delegating to the Engine and Policy.
    Contains strictly no business logic or rule evaluation.
    """

    def __init__(
        self, 
        context_factory: IMatchingContextFactory,
        engine: IMatchingEngine, 
        policy: IMatchPolicy
    ) -> None:
        """
        Initializes the service with required dependencies.

        Args:
            context_factory (IMatchingContextFactory): The factory to build the MatchingContext.
            engine (IMatchingEngine): The deterministic matching engine.
            policy (IMatchPolicy): The business interpretation policy.
        """
        self._context_factory = context_factory
        self._engine = engine
        self._policy = policy

    def evaluate_match(
        self, 
        request: MatchRequest, 
        campaign: Campaign, 
        knowledge: List[KnowledgeEntry]
    ) -> MatchingOutcome:
        """
        Coordinates the evaluation of a match request.

        Args:
            request (MatchRequest): The parameters defining the match evaluation.
            campaign (Campaign): The campaign being evaluated.
            knowledge (List[KnowledgeEntry]): The relevant knowledge entries.

        Returns:
            MatchingOutcome: The structured outcome encapsulating the request, result, and business decision.
            
        Raises:
            MatchingServiceError: If an error occurs during orchestration.
        """
        try:
            # 1. Construct Domain Context via Factory
            context = self._context_factory.create(
                request=request, 
                campaign=campaign, 
                knowledge=knowledge
            )

            # 2. Invoke Engine (Rule Evaluation)
            match_result = self._engine.evaluate(context)

            # 3. Invoke Policy (Business Interpretation)
            policy_decision = self._policy.evaluate(match_result)

            # 4. Construct Final Outcome
            outcome = MatchingOutcome(
                request=request,
                result=match_result,
                decision=policy_decision
            )

            return outcome

        except MatchingException as e:
            # Re-raise domain-specific exceptions directly or wrap them depending on preference.
            # Wrapping them ensures a consistent service boundary.
            raise MatchingServiceError(f"Matching domain error during service orchestration: {str(e)}") from e
        except Exception as e:
            # Catch unexpected exceptions and wrap them to maintain service boundary
            raise MatchingServiceError(f"Unexpected error during matching service orchestration: {str(e)}") from e
