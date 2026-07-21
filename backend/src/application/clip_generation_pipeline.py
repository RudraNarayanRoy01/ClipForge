import logging
from src.editing.domain.models.project import EditingProject
from src.editing.domain.models.state import TimelineState
from src.domain.models.rendering import RenderSettings
from src.domain.models.export import ExportSettings, ExportRequest

from src.editing.domain.services.editing_pipeline_service import IEditingPipelineService
from src.editing.domain.services.timeline_execution_pipeline import ITimelineExecutionPipeline
from src.application.rendering_backend import RenderingBackend
from src.application.export_pipeline import ExportPipeline

from datetime import datetime, timezone
from dataclasses import dataclass, field
from src.domain.campaign_entities import ExecutionStatus

@dataclass
class ClipGenerationResult:
    project_id: str
    execution_status: ExecutionStatus = ExecutionStatus.CREATED
    execution_status_updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    export_result: getattr(ExportPipeline, 'ReturnType', object) = None
    error: getattr(Exception, 'ReturnType', str) = None
    
    def transition_execution_state(self, new_status: ExecutionStatus) -> None:
        terminal_states = {ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED}
        if self.execution_status in terminal_states and new_status not in {ExecutionStatus.CREATED, ExecutionStatus.INITIALIZED}:
             raise ValueError(f"Cannot transition from terminal state {self.execution_status} to {new_status}")
        self.execution_status = new_status
        self.execution_status_updated_at = datetime.now(timezone.utc)

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
    ) -> ClipGenerationResult:
        """
        Executes the coherent end-to-end workflow for clip generation.
        Natural exceptions are allowed to propagate to the workflow dispatcher.
        """
        result = ClipGenerationResult(project_id=str(project.id))
        result.transition_execution_state(ExecutionStatus.INITIALIZED)
        
        logger.info("ClipGenerationPipeline started", extra={"project_id": str(project.id)})
        
        try:
            result.transition_execution_state(ExecutionStatus.RUNNING)
            
            # Invariant: Editing cannot execute before timeline context
            if not project.timeline or not initial_state:
                raise ValueError("Lifecycle Invariant Violation: Editing cannot execute before timeline context is initialized.")
                
            # 1. AI Editing Strategy & Operations Transformation
            logger.info("Stage: Editing Pipeline")
            editing_result = await self._editing_pipeline.run_pipeline(project)
            
            # 2. Timeline Execution (Applying operations to state)
            logger.info("Stage: Timeline Execution")
            final_timeline_state = await self._timeline_execution.execute(
                state=initial_state,
                transformation_result=editing_result.transformation_result
            )
            
            # Invariant: Render planning must precede execution
            if not render_settings:
                raise ValueError("Lifecycle Invariant Violation: Render planning settings are required before rendering.")
            
            # 3. Rendering
            logger.info("Stage: Rendering")
            render_result = self._rendering_backend.render(
                timeline_state=final_timeline_state,
                render_settings=render_settings
            )
            
            # Invariant: Export cannot execute before render completes
            if not render_result or not render_result.artifact_uri:
                 raise ValueError("Lifecycle Invariant Violation: Export cannot execute before render planning and execution is complete.")
            
            # 4. Export
            logger.info("Stage: Export")
            export_request = ExportRequest(
                source_media_location=render_result.artifact_uri,
                settings=export_settings
            )
            export_result = self._export_pipeline.execute(export_request)
            result.export_result = export_result
            
            result.transition_execution_state(ExecutionStatus.COMPLETED)
            logger.info("ClipGenerationPipeline completed successfully", extra={"export_status": export_result.status.value})
            return result
        except Exception as e:
            result.transition_execution_state(ExecutionStatus.FAILED)
            result.error = str(e)
            logger.error("ClipGenerationPipeline failed", extra={"project_id": str(project.id), "error": str(e)}, exc_info=True)
            raise
