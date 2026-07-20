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
    async def build_clip(
        self, 
        asset_id: UUID, 
        source_time_range: TimeRange, 
        target_time_range: TimeRange
    ) -> Clip:
        """
        Constructs a Clip timeline item for the given asset and timing boundaries.
        """
        pass
