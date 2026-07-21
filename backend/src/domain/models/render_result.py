from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any


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
class RenderResult:
    """
    Represents the canonical outcome of rendering execution.
    
    Contains domain information only, without implementation-specific handles
    (e.g., MoviePy, FFmpeg, filesystem, GPU, CPU).
    """
    status: RenderStatus
    rendered_output_location: Optional[str] = None
    rendered_duration: Optional[float] = None
    rendering_metadata: Dict[str, Any] = field(default_factory=dict)
    message: Optional[str] = None
