from dataclasses import dataclass

from src.editing.domain.enums.export import ExportQuality, Orientation
from src.editing.domain.value_objects.spatial import VideoResolution


@dataclass(frozen=True)
class ExportProfile:
    """
    Expresses desired output characteristics without renderer-specific details.
    """
    orientation: Orientation
    resolution: VideoResolution
    frame_rate: float
    quality_preference: ExportQuality
