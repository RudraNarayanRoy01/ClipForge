from src.application.execution_models import ValidatedRenderPlan
from src.infrastructure.rendering.moviepy.structures import MoviePyRenderTask

class MoviePyRequestTranslator:
    """
    Translates application-level validated render plans into 
    MoviePy-specific rendering tasks.
    
    This translation is strictly one-way (ValidatedRenderPlan -> MoviePyRenderTask).
    Its responsibility ends after producing the task.
    """
    
    def translate(self, validated_plan: ValidatedRenderPlan, output_destination: str) -> MoviePyRenderTask:
        """
        Translates the validated plan into a MoviePyRenderTask.
        
        Args:
            validated_plan: The ValidatedRenderPlan containing the canonical render plan.
            output_destination: The destination path for the rendered output.
            
        Returns:
            MoviePyRenderTask: The backend-specific task structure.
        """
        plan = validated_plan.plan
        
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
