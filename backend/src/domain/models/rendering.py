from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any

from src.domain.entities import Resolution

from src.domain.models.render_result import RenderStatus, RenderResult

@dataclass(frozen=True)
class RenderSettings:
    """
    Encapsulates the configuration required to render a video.
    Describes 'how' rendering should occur without performing the rendering itself.
    """
    output_resolution: Resolution
    frame_rate: float
    video_codec: str
    audio_codec: str
    bitrate: str
    output_format: str
    # Where rendering writes the produced artifact. Not the final user-facing export destination.
    render_output_location: str
