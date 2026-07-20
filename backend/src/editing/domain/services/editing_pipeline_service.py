from abc import ABC, abstractmethod

from src.editing.domain.models.project import EditingProject
from src.editing.domain.models.pipeline import EditingPipelineResult


class IEditingPipelineService(ABC):
    """
    The central orchestration boundary for the editing subsystem.
    
    Coordinates the underlying strategy, transformation, and validation 
    services to produce a comprehensive EditingPipelineResult. Exposes 
    a single public entry point for the editing workflow while keeping 
    business logic delegated to the appropriate domain services.
    """

    @abstractmethod
    async def run_pipeline(self, project: EditingProject) -> EditingPipelineResult:
        """
        Executes the editing pipeline workflow for a given project.
        
        Args:
            project: The editing project containing the timeline and parameters.
            
        Returns:
            EditingPipelineResult containing the plan, transformation, and validation.
        """
        pass
