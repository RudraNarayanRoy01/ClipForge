import uuid
from typing import Dict, Any

try:
    from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip
except ImportError:
    # Handle environment without moviepy for tests or graceful failure
    VideoFileClip = None
    AudioFileClip = None
    ImageClip = None

from src.domain.render_plan import RenderPlan, LayerCategory
from src.infrastructure.rendering.moviepy.structures import MoviePyResourcePool
from src.infrastructure.rendering.moviepy.validation import MoviePyAssetValidator

class MoviePyAssetLoader:
    """
    Resolves and loads media references into backend-owned runtime resources.
    
    Remains stateless. It populates a provided MoviePyResourcePool with handles 
    to the loaded resources (e.g., VideoFileClip, AudioFileClip), but does not 
    compose them or track their timeline sequence.
    """
    
    @classmethod
    def load_assets(cls, plan: RenderPlan, pool: MoviePyResourcePool) -> None:
        """
        Iterates over the render plan, validates assets, and loads them into the pool.
        
        Args:
            plan: The canonical render plan containing media references.
            pool: The resource pool to populate with loaded handles.
            
        Raises:
            Exception: Any filesystem or MoviePy exceptions are allowed to propagate
                       up to be translated by the backend exception translator.
        """
        for layer in plan.layers:
            # Map layer category to expected validation category
            expected_category = cls._map_layer_category(layer.category)
            
            for track in layer.tracks:
                for segment in track.segments:
                    source_ref = segment.source_reference
                    segment_id = segment.id
                    
                    # 1. Validation
                    MoviePyAssetValidator.validate_reference(source_ref, expected_category)
                    
                    # 2. Loading
                    clip = cls._load_clip(source_ref, expected_category)
                    
                    # 3. Ownership transfer
                    if clip is not None:
                        cls._register_clip(pool, expected_category, segment_id, clip)
                    else:
                        # For example, subtitle structures might just store the path or raw data
                        pool.add_generic_resource(segment_id, {"type": "subtitle", "path": source_ref})

    @classmethod
    def _map_layer_category(cls, category: LayerCategory) -> str:
        if category == LayerCategory.VIDEO:
            return "video"
        elif category == LayerCategory.AUDIO:
            return "audio"
        elif category == LayerCategory.SUBTITLE:
            return "subtitle"
        elif category == LayerCategory.OVERLAY:
            return "image" # Assuming overlays are mostly images in this basic model
        return "video"

    @classmethod
    def _load_clip(cls, source_reference: str, category: str) -> Any:
        """
        Instantiates the actual MoviePy clip object.
        """
        if VideoFileClip is None:
            raise RuntimeError("moviepy is not installed or available.")
            
        if category == "video":
            return VideoFileClip(source_reference)
        elif category == "audio":
            return AudioFileClip(source_reference)
        elif category == "image":
            return ImageClip(source_reference)
        elif category == "subtitle":
            # Subtitles are not loaded as MoviePy clips directly in this batch
            # They will be processed as structural data later.
            return None
            
        raise ValueError(f"Cannot load unsupported category '{category}'")

    @classmethod
    def _register_clip(cls, pool: MoviePyResourcePool, category: str, resource_id: uuid.UUID, clip: Any) -> None:
        if category == "video":
            pool.add_video_clip(resource_id, clip)
        elif category == "audio":
            pool.add_audio_clip(resource_id, clip)
        elif category == "image":
            pool.add_image_clip(resource_id, clip)
