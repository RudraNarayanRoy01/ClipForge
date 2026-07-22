import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from src.domain.render_plan import RenderPlan

@dataclass
class MoviePyResourcePool:
    """
    Manages ownership and lifecycle of MoviePy resources.
    
    This class defines the ownership boundaries for resources that will be
    instantiated during the rendering process. It does not instantiate or 
    manage live MoviePy clip objects in this batch. Actual resource allocation 
    belongs to Batch 5.5.5.2.
    """
    video_clips: Dict[uuid.UUID, Any] = field(default_factory=dict)
    audio_clips: Dict[uuid.UUID, Any] = field(default_factory=dict)
    image_clips: Dict[uuid.UUID, Any] = field(default_factory=dict)
    temporary_files: List[str] = field(default_factory=list)

    def register_temp_file(self, file_path: str) -> None:
        """Registers a temporary file for later cleanup."""
        self.temporary_files.append(file_path)

    def cleanup(self) -> None:
        """
        Releases all held MoviePy resources and deletes temporary files.
        (Implementation deferred to Batch 5.5.5.2)
        """
        # Close all clip resources
        self.video_clips.clear()
        self.audio_clips.clear()
        self.image_clips.clear()
        
        # Temp file deletion would happen here
        self.temporary_files.clear()


@dataclass
class MoviePyRenderTask:
    """
    A backend-specific representation of a rendering task.
    
    It maps the attributes of a ValidatedRenderPlan into MoviePy-friendly 
    internal state, acting as the single source of truth for a rendering execution
    within the MoviePy backend.
    """
    # The original plan is kept for reference, but backend-specific translation
    # fields would be populated here.
    original_plan_id: uuid.UUID
    output_destination: str
    
    # Internal representation of the timeline mapping
    # (e.g., layers, tracks, ordered by z-index or time)
    video_tracks_data: List[Any] = field(default_factory=list)
    audio_tracks_data: List[Any] = field(default_factory=list)
    overlay_tracks_data: List[Any] = field(default_factory=list)
    subtitle_tracks_data: List[Any] = field(default_factory=list)
    
    resolution_width: int = 1920
    resolution_height: int = 1080
    fps: float = 30.0
    
    # Resources owned by this task
    resources: MoviePyResourcePool = field(default_factory=MoviePyResourcePool)
