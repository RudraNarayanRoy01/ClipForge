from abc import ABC, abstractmethod

from src.editing.domain.models.plan import EditingPlan
from src.editing.domain.models.transformation import TimelineTransformationResult


class ITimelineTransformationService(ABC):
    """
    Architectural boundary for transforming an EditingPlan into a TimelineTransformationResult.
    Responsible for converting editorial intent into backend-independent timeline operations.
    """

    @abstractmethod
    async def transform(self, plan: EditingPlan) -> TimelineTransformationResult:
        """
        Transforms an EditingPlan into a sequence of TimelineOperations.
        """
        pass
