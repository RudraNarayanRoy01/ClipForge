import logging
from src.editing.domain.models.project import EditingProject
from src.editing.domain.models.state import TimelineState
from src.domain.models.render_profile import RenderProfile
from src.domain.models.export import ExportSettings, ExportRequest

from src.editing.orchestration.interfaces import IEditingOrchestrator
from src.editing.orchestration.commands import EditingExecutionCommand
from src.application.render_planning_pipeline import RenderPlanningPipeline
from src.application.render_execution_service import RenderExecutionService
from src.application.execution_models import ValidatedRenderPlan
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
    
    Coordinates the canonical execution stages:
    1. AI Editing Strategy & Transformation (IEditingOrchestrator)
    2. Render Planning (RenderPlanningPipeline)
    3. Rendering Execution (RenderExecutionService)
    4. Export (ExportPipeline)
    
    This reflects the fully certified architecture chain.
    """
    
    def __init__(
        self,
        editing_orchestrator: IEditingOrchestrator,
        render_planning_pipeline: RenderPlanningPipeline,
        render_execution_service: RenderExecutionService,
        export_pipeline: ExportPipeline
    ):
        self._editing_orchestrator = editing_orchestrator
        self._render_planning_pipeline = render_planning_pipeline
        self._render_execution_service = render_execution_service
        self._export_pipeline = export_pipeline
        
    async def execute_workflow(
        self,
        project: EditingProject,
        render_profile: RenderProfile,
        export_settings: ExportSettings,
        output_destination: str
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
                
            # 1. AI Editing Strategy & Operations Transformation -> Yields FinalizedEdit
            logger.info("Stage: Editing Pipeline (Orchestrator)")
            editing_command = EditingExecutionCommand(project=project)
            editing_result = await self._editing_orchestrator.execute(editing_command)
            
            finalized_edit = editing_result.finalized_edit
            
            # 2. Render Planning -> Yields RenderPlan
            logger.info("Stage: Render Planning")
            render_plan = self._render_planning_pipeline.execute(
                finalized_edit=finalized_edit,
                render_profile=render_profile
            )
            
            # Wrap in ValidatedRenderPlan (trusting the pipeline)
            validated_plan = ValidatedRenderPlan(
                plan=render_plan,
                validated_at=datetime.now(timezone.utc)
            )
            
            # 3. Rendering Execution -> Delegates to IRenderBackend
            logger.info("Stage: Rendering Execution")
            render_result = await self._render_execution_service.execute_plan(
                validated_plan=validated_plan,
                output_destination=output_destination
            )
            
            if render_result.status.value != "completed":
                raise RuntimeError(f"Rendering failed: {render_result.diagnostics.message if render_result.diagnostics else 'Unknown error'}")
            
            # 4. Export
            logger.info("Stage: Export")
            export_request = ExportRequest(
                source_media_location=render_result.output_artifact_path,
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
