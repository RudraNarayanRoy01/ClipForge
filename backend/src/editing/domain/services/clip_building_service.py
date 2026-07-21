from abc import ABC, abstractmethod

from src.editing.domain.models.items import Clip
from src.editing.domain.models.project import EditingProject
from src.editing.domain.models.timeline import Timeline
from typing import List

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
