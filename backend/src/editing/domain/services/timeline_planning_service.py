from abc import ABC, abstractmethod

from src.editing.domain.models.project import EditingProject
from src.editing.domain.models.timeline import Timeline


class ITimelinePlanningService(ABC):
    """
    Service contract for organizing the timeline.
    Defines capabilities without implementing heuristics or AI logic.
    """

    @abstractmethod
    async def plan_timeline(self, project: EditingProject) -> Timeline:
        """
        Produces or updates a Timeline based on the given EditingProject.
        """
        pass
