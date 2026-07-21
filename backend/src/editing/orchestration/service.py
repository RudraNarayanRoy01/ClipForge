from src.editing.domain.models.project import EditingProject
from src.editing.domain.pipeline.clips import ClipSequence
from src.editing.domain.pipeline.editing import EditingSequence
from src.editing.domain.pipeline.export import RenderPlan
from src.editing.domain.pipeline.subtitles import SubtitleTrack
from src.editing.domain.pipeline.timeline import TimelinePlanningResult
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

    async def execute(
        self,
        command: EditingExecutionCommand,
    ) -> EditingExecutionResult:
        """
        Coordinates the complete editing workflow.
        """
        timeline_result = await self._plan_timeline(command.project)
        clip_sequence = await self._build_clips(command.project, timeline_result)
        editing_sequence = await self._generate_edit_sequence(command.project, clip_sequence)
        subtitle_track = await self._generate_subtitles(command.project)
        render_plan = await self._plan_export(command.project, editing_sequence, subtitle_track)

        return EditingExecutionResult(
            render_plan=render_plan,
        )

    async def _plan_timeline(
        self,
        project: EditingProject,
    ) -> TimelinePlanningResult:
        timeline = await self._timeline_planning_service.plan_timeline(project)
        return TimelinePlanningResult(timeline=timeline)

    async def _build_clips(
        self,
        project: EditingProject,
        timeline_result: TimelinePlanningResult,
    ) -> ClipSequence:
        clips = await self._clip_building_service.build_clips(project, timeline_result.timeline)
        return ClipSequence(clips=clips)

    async def _generate_edit_sequence(
        self,
        project: EditingProject,
        clip_sequence: ClipSequence,
    ) -> EditingSequence:
        metadata = await self._editing_service.generate_edit_sequence(project, clip_sequence.clips)
        return EditingSequence(metadata=metadata)

    async def _generate_subtitles(
        self,
        project: EditingProject,
    ) -> SubtitleTrack:
        import uuid
        subtitles = await self._subtitle_generation_service.generate_subtitles(project)
        return SubtitleTrack(id=uuid.uuid4(), subtitles=subtitles)

    async def _plan_export(
        self,
        project: EditingProject,
        editing_sequence: EditingSequence,
        subtitle_track: SubtitleTrack,
    ) -> RenderPlan:
        export_profile = await self._export_planning_service.plan_export(project)
        return RenderPlan(
            editing_sequence=editing_sequence,
            subtitle_track=subtitle_track,
            export_profile=export_profile
        )
