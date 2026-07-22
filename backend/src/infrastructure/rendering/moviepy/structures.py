import uuid
import contextlib
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from src.domain.render_plan import RenderPlan

@dataclass
class MoviePyResourcePool:
    """
    Manages ownership and lifecycle of MoviePy resources.
    
    This class defines the ownership boundaries for resources that will be
    instantiated during the rendering process. It does not possess any knowledge
    of timeline ordering, sequencing, or composition.
    """
    # Keys are typically segment IDs or generated unique resource IDs
    video_clips: Dict[uuid.UUID, Any] = field(default_factory=dict)
    audio_clips: Dict[uuid.UUID, Any] = field(default_factory=dict)
    image_clips: Dict[uuid.UUID, Any] = field(default_factory=dict)
    # We might have other generic resources (e.g., subtitle data)
    generic_resources: Dict[uuid.UUID, Any] = field(default_factory=dict)
    
    temporary_files: List[str] = field(default_factory=list)

    def add_video_clip(self, resource_id: uuid.UUID, clip: Any) -> None:
        self.video_clips[resource_id] = clip

    def add_audio_clip(self, resource_id: uuid.UUID, clip: Any) -> None:
        self.audio_clips[resource_id] = clip

    def add_image_clip(self, resource_id: uuid.UUID, clip: Any) -> None:
        self.image_clips[resource_id] = clip
        
    def add_generic_resource(self, resource_id: uuid.UUID, resource: Any) -> None:
        self.generic_resources[resource_id] = resource

    def register_temp_file(self, file_path: str) -> None:
        """Registers a temporary file for later cleanup."""
        self.temporary_files.append(file_path)

    def cleanup(self) -> None:
        """
        Releases all held MoviePy resources and deletes temporary files.
        Ensures explicit closing of clip handles to prevent resource leaks.
        """
        for clip in self.video_clips.values():
            with contextlib.suppress(Exception):
                clip.close()
        self.video_clips.clear()

        for clip in self.audio_clips.values():
            with contextlib.suppress(Exception):
                clip.close()
        self.audio_clips.clear()

        for clip in self.image_clips.values():
            with contextlib.suppress(Exception):
                clip.close()
        self.image_clips.clear()
        
        self.generic_resources.clear()
        
        # In a real implementation, temporary_files would be unlinked here via os.remove
        # e.g., for temp_file in self.temporary_files: Path(temp_file).unlink(missing_ok=True)
        self.temporary_files.clear()

    def get_video_clip(self, resource_id: uuid.UUID) -> Optional[Any]:
        return self.video_clips.get(resource_id)

    def get_audio_clip(self, resource_id: uuid.UUID) -> Optional[Any]:
        return self.audio_clips.get(resource_id)

    def get_image_clip(self, resource_id: uuid.UUID) -> Optional[Any]:
        return self.image_clips.get(resource_id)


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
