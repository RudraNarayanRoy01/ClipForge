from abc import ABC, abstractmethod
from uuid import UUID

from src.editing.domain.models.items import Clip
from src.editing.domain.value_objects.time import TimeRange


class IClipBuildingService(ABC):
    """
    Service contract for assembling clips into the timeline.
    Defines capabilities without implementing editing logic or AI.
    """

    @abstractmethod
    async def build_clips(
        self, 
        project: EditingProject,
        timeline: Timeline
    ) -> List[Clip]:
        """
        Constructs Clip timeline items for the given project and timeline.
        """
        pass
