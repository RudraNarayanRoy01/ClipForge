import logging
from src.editing.domain.models.project import EditingProject
from src.editing.domain.models.state import TimelineState
from src.domain.models.rendering import RenderSettings
from src.domain.models.export import ExportSettings, ExportRequest

from src.editing.domain.services.editing_pipeline_service import IEditingPipelineService
from src.editing.domain.services.timeline_execution_pipeline import ITimelineExecutionPipeline
from src.application.rendering_backend import RenderingBackend
from src.application.export_pipeline import ExportPipeline

logger = logging.getLogger(__name__)

class ClipGenerationPipelineService:
    """
    Top-level orchestrator for the Clip Generation Pipeline.
    
    Coordinates the four independent execution stages:
    1. AI Editing Strategy & Transformation (IEditingPipelineService)
    2. Timeline Execution (ITimelineExecutionPipeline)
    3. Rendering (RenderingBackend)
    4. Export (ExportPipeline)
    
    This preserves independent ownership while maintaining deterministic execution sequence.
    """
    
    def __init__(
        self,
        editing_pipeline: IEditingPipelineService,
        timeline_execution: ITimelineExecutionPipeline,
        rendering_backend: RenderingBackend,
        export_pipeline: ExportPipeline
    ):
        self._editing_pipeline = editing_pipeline
        self._timeline_execution = timeline_execution
        self._rendering_backend = rendering_backend
        self._export_pipeline = export_pipeline
        
    async def execute_workflow(
        self,
        project: EditingProject,
        initial_state: TimelineState,
        render_settings: RenderSettings,
        export_settings: ExportSettings
    ) -> None:
        """
        Executes the coherent end-to-end workflow for clip generation.
        Natural exceptions are allowed to propagate to the workflow dispatcher.
        """
        logger.info("ClipGenerationPipeline started", extra={"project_id": str(project.id)})
        
        # 1. AI Editing Strategy & Operations Transformation
        logger.info("Stage: Editing Pipeline")
        editing_result = await self._editing_pipeline.run_pipeline(project)
        
        # 2. Timeline Execution (Applying operations to state)
        logger.info("Stage: Timeline Execution")
        final_timeline_state = await self._timeline_execution.execute(
            state=initial_state,
            transformation_result=editing_result.transformation_result
        )
        
        # 3. Rendering
        logger.info("Stage: Rendering")
        render_result = self._rendering_backend.render(
            timeline_state=final_timeline_state,
            render_settings=render_settings
        )
        
        # 4. Export
        logger.info("Stage: Export")
        export_request = ExportRequest(
            source_media_location=render_result.artifact_uri,
            settings=export_settings
        )
        export_result = self._export_pipeline.execute(export_request)
        
        logger.info("ClipGenerationPipeline completed successfully", extra={"export_status": export_result.status.value})
