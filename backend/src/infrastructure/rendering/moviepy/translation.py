from src.domain.render_plan import RenderPlan
from src.infrastructure.rendering.moviepy.structures import MoviePyRenderTask

class MoviePyRequestTranslator:
    """
    Translates domain render plans into 
    MoviePy-specific rendering tasks.
    
    This translation is strictly one-way (RenderPlan -> MoviePyRenderTask).
    Its responsibility ends after producing the task.
    """
    
    def translate(self, plan: RenderPlan, output_destination: str) -> MoviePyRenderTask:
        """
        Translates the render plan into a MoviePyRenderTask.
        
        Args:
            plan: The canonical render plan.
            output_destination: The destination path for the rendered output.
            
        Returns:
            MoviePyRenderTask: The backend-specific task structure.
        """
        
        task = MoviePyRenderTask(
            original_plan_id=plan.id,
            output_destination=output_destination,
            resolution_width=plan.metadata.resolution.width,
            resolution_height=plan.metadata.resolution.height,
            fps=plan.metadata.frame_rate.fps
        )
        
        # In the future (Batch 5.5.5.2), we will map timeline states 
        # (video, audio, overlay, subtitle tracks) into task.*_tracks_data
        
        return task
