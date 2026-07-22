import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, Optional

from src.infrastructure.rendering.moviepy.timeline import MoviePyTimeline
from src.infrastructure.rendering.moviepy.validation import MoviePyOutputValidator


@dataclass(frozen=True)
class MoviePyRenderConfiguration:
    """
    Immutable representation of codec-independent render settings and 
    execution parameters for MoviePy rendering.
    """
    fps: float
    resolution: Tuple[int, int]
    background_color: Tuple[int, int, int] = (0, 0, 0)
    # Future platform-specific or codec-specific rendering options can go here


@dataclass(frozen=True)
class MoviePyRenderOutput:
    """
    Immutable render specification.
    
    References the composition graph (timeline) and configuration.
    Semantically backend-neutral in its intent, acting as a specification for the execution engine.
    Does NOT own execution resources or define filesystem destinations, which remain an execution concern.
    """
    id: uuid.UUID
    timeline: MoviePyTimeline
    configuration: MoviePyRenderConfiguration
    metadata: Dict[str, Any] = field(default_factory=dict)


class MoviePyOutputComposer:
    """
    Responsible for transforming a validated MoviePyTimeline into an immutable
    MoviePyRenderOutput specification.
    
    Remains strictly an infrastructure boundary concern. Never triggers rendering
    or mutating the underlying timeline graph.
    """
    
    @classmethod
    def compose_output(
        cls, 
        timeline: MoviePyTimeline, 
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> MoviePyRenderOutput:
        """
        Validates the timeline and prepares a deterministic render specification.
        
        Args:
            timeline: The immutable timeline to be rendered.
            custom_metadata: Optional additional metadata for the render output.
            
        Returns:
            An immutable MoviePyRenderOutput ready for the execution layer.
            
        Raises:
            ValueError: If the timeline fails validation semantics.
        """
        # Validate semantics (does not check filesystem/execution concerns)
        MoviePyOutputValidator.validate_timeline(timeline)
        
        # Prepare render configuration based on timeline context
        config = MoviePyRenderConfiguration(
            fps=timeline.context.fps,
            resolution=(timeline.context.resolution_width, timeline.context.resolution_height),
            background_color=timeline.context.background_color
        )
        
        # Consolidate metadata
        metadata = {
            "duration_seconds": timeline.context.duration_seconds,
            "has_video": timeline.has_video,
            "has_audio": timeline.has_audio,
        }
        if custom_metadata:
            metadata.update(custom_metadata)
            
        # Produce new immutable output object
        return MoviePyRenderOutput(
            id=uuid.uuid4(),
            timeline=timeline,
            configuration=config,
            metadata=metadata
        )
