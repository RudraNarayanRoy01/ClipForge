from src.editing.domain.models.plan import EditingPlan
from src.editing.domain.models.transformation import TimelineTransformationResult
from src.editing.domain.services.transformation import ITimelineTransformationService


class DefaultTimelineTransformationService(ITimelineTransformationService):
    """
    Default implementation of the timeline transformation engine.
    Establishes the boundary by validating the plan and returning a deterministic result.
    Does not perform media manipulation or actual timeline rendering.
    """

    async def transform(self, plan: EditingPlan) -> TimelineTransformationResult:
        """
        Transforms an EditingPlan into a sequence of TimelineOperations.
        Currently a placeholder that validates the boundary without side effects.
        """
        if not plan:
            raise ValueError("EditingPlan cannot be None")
        
        # Returns an empty result to establish the architectural boundary
        # Future strategies (e.g., ClipTransformationStrategy) will be invoked here.
        return TimelineTransformationResult(operations=())
