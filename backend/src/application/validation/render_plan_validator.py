from typing import List

from src.domain.render_plan import RenderPlan, RenderLayer, RenderTrack, RenderSegment, RenderInstruction
from src.application.validation.models import RenderValidationIssue, RenderValidationResult


class RenderPlanValidator:
    """
    Validates a RenderPlan for structural and logical consistency.
    This validator operates purely on the Application layer, ensuring that the 
    RenderPlan aggregate is fully formed, its metadata is valid, and its timeline
    is consistent. It does not validate renderer capabilities, semantic editing
    intent, or perform any mutations.
    """

    def validate(self, plan: RenderPlan) -> RenderValidationResult:
        issues: List[RenderValidationIssue] = []

        self._validate_aggregate_integrity(plan, issues)
        self._validate_metadata(plan, issues)
        
        # We only check layer details if there are layers to check.
        if plan.layers:
            self._validate_layers(plan.layers, plan, issues)

        return RenderValidationResult(issues=issues)

    def _validate_aggregate_integrity(self, plan: RenderPlan, issues: List[RenderValidationIssue]) -> None:
        if not plan.layers:
            issues.append(RenderValidationIssue.error(
                "RenderPlan has no layers. A valid render plan must contain at least one layer.",
                context_path=f"RenderPlan[{plan.id}]"
            ))

    def _validate_metadata(self, plan: RenderPlan, issues: List[RenderValidationIssue]) -> None:
        ctx = f"RenderPlan[{plan.id}].metadata"
        meta = plan.metadata
        
        if meta.resolution.width <= 0 or meta.resolution.height <= 0:
            issues.append(RenderValidationIssue.error(
                f"Invalid resolution: {meta.resolution.width}x{meta.resolution.height}",
                context_path=ctx
            ))
            
        if meta.frame_rate.fps <= 0:
            issues.append(RenderValidationIssue.error(
                f"Invalid framerate: {meta.frame_rate.fps}",
                context_path=ctx
            ))
            
        if meta.aspect_ratio.width_ratio <= 0 or meta.aspect_ratio.height_ratio <= 0:
            issues.append(RenderValidationIssue.error(
                f"Invalid aspect ratio: {meta.aspect_ratio.width_ratio}:{meta.aspect_ratio.height_ratio}",
                context_path=ctx
            ))
            
        if meta.duration_seconds < 0:
            issues.append(RenderValidationIssue.error(
                f"Invalid total duration: {meta.duration_seconds}s (cannot be negative)",
                context_path=ctx
            ))
        elif meta.duration_seconds == 0:
            issues.append(RenderValidationIssue.warning(
                "Total duration is 0s. This may result in an empty output.",
                context_path=ctx
            ))

    def _validate_layers(self, layers: List[RenderLayer], plan: RenderPlan, issues: List[RenderValidationIssue]) -> None:
        for layer in layers:
            ctx = f"RenderPlan[{plan.id}].Layer[{layer.id}]"
            if not layer.tracks:
                issues.append(RenderValidationIssue.info(
                    f"Layer '{layer.name}' contains no tracks.",
                    context_path=ctx
                ))
            else:
                self._validate_tracks(layer.tracks, layer, plan, issues)

    def _validate_tracks(self, tracks: List[RenderTrack], layer: RenderLayer, plan: RenderPlan, issues: List[RenderValidationIssue]) -> None:
        for track in tracks:
            ctx = f"RenderPlan[{plan.id}].Layer[{layer.id}].Track[{track.id}]"
            if not track.segments:
                issues.append(RenderValidationIssue.info(
                    f"Track '{track.name}' contains no segments.",
                    context_path=ctx
                ))
            else:
                self._validate_segments(track.segments, track, layer, plan, issues)

    def _validate_segments(self, segments: List[RenderSegment], track: RenderTrack, layer: RenderLayer, plan: RenderPlan, issues: List[RenderValidationIssue]) -> None:
        # Validate that segments are ordered by start time
        for i in range(1, len(segments)):
            prev = segments[i-1]
            curr = segments[i]
            if curr.timeline_start.time_seconds < prev.timeline_start.time_seconds:
                ctx = f"RenderPlan[{plan.id}].Layer[{layer.id}].Track[{track.id}]"
                issues.append(RenderValidationIssue.error(
                    f"Segments are out of order: Segment {curr.id} starts before Segment {prev.id}.",
                    context_path=ctx
                ))

        for segment in segments:
            ctx = f"RenderPlan[{plan.id}].Layer[{layer.id}].Track[{track.id}].Segment[{segment.id}]"
            
            # Validate chronological ordering within the segment
            if segment.timeline_end.time_seconds < segment.timeline_start.time_seconds:
                issues.append(RenderValidationIssue.error(
                    "timeline_end occurs before timeline_start.",
                    context_path=ctx
                ))
                
            if segment.source_end.time_seconds < segment.source_start.time_seconds:
                issues.append(RenderValidationIssue.error(
                    "source_end occurs before source_start.",
                    context_path=ctx
                ))

            # Validate positive durations
            timeline_duration = segment.timeline_end.time_seconds - segment.timeline_start.time_seconds
            if timeline_duration < 0:
                # Already caught above, but conceptually distinct
                pass 
            elif timeline_duration == 0:
                issues.append(RenderValidationIssue.warning(
                    "Segment has a timeline duration of 0s.",
                    context_path=ctx
                ))
                
            # Validate bounds
            if segment.timeline_end.time_seconds > plan.metadata.duration_seconds:
                issues.append(RenderValidationIssue.error(
                    f"Segment extends beyond the total render duration ({segment.timeline_end.time_seconds}s > {plan.metadata.duration_seconds}s).",
                    context_path=ctx
                ))
                
            # Validate instructions structurally
            for idx, instruction in enumerate(segment.instructions):
                self._validate_instruction(instruction, idx, ctx, issues)

    def _validate_instruction(self, instruction: RenderInstruction, idx: int, parent_ctx: str, issues: List[RenderValidationIssue]) -> None:
        ctx = f"{parent_ctx}.Instruction[{idx}]"
        
        # Must have an instruction type
        if not instruction.instruction_type or not instruction.instruction_type.strip():
            issues.append(RenderValidationIssue.error(
                "Instruction is missing an instruction_type.",
                context_path=ctx
            ))
            
        # Must have a parameters dictionary
        if instruction.parameters is None:
            issues.append(RenderValidationIssue.error(
                "Instruction parameters must be a dictionary, not None.",
                context_path=ctx
            ))
        elif not isinstance(instruction.parameters, dict):
             issues.append(RenderValidationIssue.error(
                f"Instruction parameters must be a dictionary, got {type(instruction.parameters).__name__}.",
                context_path=ctx
            ))
