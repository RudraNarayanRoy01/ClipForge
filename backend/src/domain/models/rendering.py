from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any

from src.domain.entities import Resolution

class RenderStatus(str, Enum):
    """
    Represents the lifecycle state of a rendering job.
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


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


@dataclass(frozen=True)
class RenderResult:
    """
    Represents the outcome of a rendering request.
    Contains domain information only, without implementation-specific handles.
    """
    status: RenderStatus
    rendered_output_location: Optional[str] = None
    rendered_duration: Optional[float] = None
    rendering_metadata: Dict[str, Any] = field(default_factory=dict)
    message: Optional[str] = None
