from src.application.export_pipeline import ExportPipeline
from src.domain.models.export import ExportRequest, ExportResult


class ExportBackend:
    """
    Public application-facing façade for the export subsystem.
    
    Exposes export capabilities to the rest of ClipForge while delegating
    all orchestration and execution details to the ExportPipeline. 
    It serves as the single entry point for exporting.
    """

    def __init__(self, pipeline: ExportPipeline):
        """
        Initializes the ExportBackend.
        
        Args:
            pipeline: The ExportPipeline responsible for coordinating export requests.
        """
        self._pipeline = pipeline

    def export(self, request: ExportRequest) -> ExportResult:
        """
        Executes an export request.
        
        Delegates the export execution to the underlying ExportPipeline. Any failures
        are allowed to propagate naturally without introducing retry or recovery logic.
        
        Args:
            request: The export request detailing source media and settings.
            
        Returns:
            ExportResult: The result of the export process.
        """
        return self._pipeline.execute(request)
