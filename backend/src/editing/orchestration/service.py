from src.editing.domain.models.project import EditingProject
from src.editing.domain.pipeline.clips import ClipBuildingRequest, ClipSequence
from src.editing.domain.pipeline.editing import EditingRequest, EditingSequence
from src.editing.domain.pipeline.export import ExportPlanningRequest, RenderPlan
from src.editing.domain.pipeline.subtitles import SubtitleGenerationRequest, SubtitleTrack
from src.editing.domain.pipeline.timeline import TimelinePlanningRequest, TimelinePlanningResult
from src.editing.domain.services.clip_building_service import IClipBuildingService
from src.editing.domain.services.editing_service import IEditingService
from src.editing.domain.services.export_planning_service import IExportPlanningService
from src.editing.domain.services.subtitle_generation_service import ISubtitleGenerationService
from src.editing.domain.services.timeline_planning_service import ITimelinePlanningService
from src.editing.orchestration.commands import EditingExecutionCommand
from src.editing.orchestration.interfaces import IEditingOrchestrator
from src.editing.orchestration.results import EditingExecutionResult


class DefaultEditingOrchestrator(IEditingOrchestrator):
    """
    Default implementation of the editing orchestrator.
    Coordinates the editing workflow exclusively through immutable 
    pipeline contracts and service interfaces.
    """

    def __init__(
        self,
        timeline_planning_service: ITimelinePlanningService,
        clip_building_service: IClipBuildingService,
        editing_service: IEditingService,
        subtitle_generation_service: ISubtitleGenerationService,
        export_planning_service: IExportPlanningService,
    ) -> None:
        self._timeline_planning_service = timeline_planning_service
        self._clip_building_service = clip_building_service
        self._editing_service = editing_service
        self._subtitle_generation_service = subtitle_generation_service
        self._export_planning_service = export_planning_service

    def execute(
        self,
        command: EditingExecutionCommand,
    ) -> EditingExecutionResult:
        """
        Coordinates the complete editing workflow.
        """
        timeline_result = self._plan_timeline(command.project)
        clip_sequence = self._build_clips(timeline_result)
        editing_sequence = self._generate_edit_sequence(clip_sequence)
        subtitle_track = self._generate_subtitles(editing_sequence)
        render_plan = self._plan_export(subtitle_track)

        return EditingExecutionResult(
            render_plan=render_plan,
        )

    def _plan_timeline(
        self,
        project: EditingProject,
    ) -> TimelinePlanningResult:
        request = TimelinePlanningRequest(project=project)
        return self._timeline_planning_service.plan_timeline(request)

    def _build_clips(
        self,
        timeline_result: TimelinePlanningResult,
    ) -> ClipSequence:
        request = ClipBuildingRequest(timeline=timeline_result)
        return self._clip_building_service.build_clips(request)

    def _generate_edit_sequence(
        self,
        clip_sequence: ClipSequence,
    ) -> EditingSequence:
        request = EditingRequest(clips=clip_sequence)
        return self._editing_service.generate_edit_sequence(request)

    def _generate_subtitles(
        self,
        editing_sequence: EditingSequence,
    ) -> SubtitleTrack:
        request = SubtitleGenerationRequest(sequence=editing_sequence)
        return self._subtitle_generation_service.generate_subtitles(request)

    def _plan_export(
        self,
        subtitle_track: SubtitleTrack,
    ) -> RenderPlan:
        request = ExportPlanningRequest(subtitles=subtitle_track)
        return self._export_planning_service.plan_export(request)
