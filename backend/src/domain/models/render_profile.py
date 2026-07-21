from dataclasses import dataclass

from src.domain.entities import Resolution
from src.domain.value_objects import AspectRatio


@dataclass(frozen=True)
class RenderProfile:
    """
    Defines reusable rendering presets that describe platform rendering defaults.
    
    This domain model is completely backend independent and does not contain 
    project-specific data, render execution state, or export logic.
    """
    name: str
    profile_type: str
    resolution: Resolution
    aspect_ratio: AspectRatio
    frame_rate: float
    video_codec: str
    audio_codec: str
    video_bitrate: str
    audio_bitrate: str
    sample_rate: int
    output_container: str

    def __post_init__(self):
        if self.frame_rate <= 0:
            raise ValueError("frame_rate must be greater than 0")
        if self.sample_rate <= 0:
            raise ValueError("sample_rate must be greater than 0")
