from abc import ABC, abstractmethod

from src.editing.domain.models.project import EditingProject
from src.editing.domain.models.plan import EditingPlan


class IEditingStrategyService(ABC):
    """
    Domain service interface for generating an editing plan.

    This service represents the architectural boundary for editorial reasoning.
    It receives an EditingProject (which contains the Timeline and other domain models)
    and produces an immutable EditingPlan defining the editorial intent.

    It abstracts away the complexities of AI reasoning, heuristics, and specialized
    strategies (e.g., highlights, subtitles, transitions, pacing), decoupling
    the domain layer from the actual decision-making implementations.
    """

    @abstractmethod
    async def generate_plan(self, project: EditingProject) -> EditingPlan:
        """
        Generate an EditingPlan based on the provided EditingProject.

        Args:
            project: The EditingProject representing the current state of the edit.

        Returns:
            EditingPlan: A deterministic plan containing editing decisions.
        """
        pass
