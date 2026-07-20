import uuid
from datetime import datetime, timezone

from src.reasoning.execution.composer.interfaces import IExecutionComposer
from src.reasoning.execution.composer.exceptions import CompositionInputError
from src.reasoning.execution.planner.models import ExecutionPlanDraft
from src.reasoning.execution.strategy.models import ExecutionStrategyResult
from src.reasoning.execution.validation.models import ExecutionValidationResult
from src.reasoning.execution.models import (
    ExecutionPlan,
    ExecutionStrategy,
    ExecutionValidation,
    ExecutionSegment,
    ExecutionMetadata,
    ExecutionStatus,
)
from src.reasoning.execution.validation.models import ValidationSeverity


class DefaultExecutionComposer(IExecutionComposer):
    """
    Deterministic composer that constructs the ExecutionPlan aggregate.
    It preserves strict ownership boundaries and never mutates prior artifacts.
    """

    def compose_execution_plan(
        self,
        plan_id: uuid.UUID,
        draft: ExecutionPlanDraft,
        strategy: ExecutionStrategyResult,
        validation: ExecutionValidationResult,
    ) -> ExecutionPlan:
        # Cross-check the strategy was generated for the exact same draft
        if strategy.execution_plan_draft is not draft:
            raise CompositionInputError(
                "ExecutionStrategyResult does not match the provided ExecutionPlanDraft."
            )

        # 1. Identity
        # The identity (plan_id) is explicitly supplied by the caller,
        # ensuring the Composer does not take responsibility for identity generation policies.

        # 2. Strategy Mapping
        # Maps the complex editorial intent to the flattened ExecutionStrategy model
        execution_strategy = ExecutionStrategy(
            hook_style=strategy.editorial_intent.hook_strategy.name,
            pacing=strategy.editorial_intent.pacing_profile.name,
            narrative_flow=strategy.editorial_intent.narrative_flow.name,
            subtitle_style=strategy.editorial_intent.subtitle_strategy.name,
            cta_style=strategy.editorial_intent.cta_strategy.name,
            aspect_ratio_preference=strategy.editorial_intent.aspect_ratio_strategy.name,
        )

        # 3. Validation Mapping
        # Separate issues based on severity
        warnings = tuple(
            issue.message for issue in validation.issues 
            if issue.severity == ValidationSeverity.WARNING
        )
        errors = tuple(
            issue.message for issue in validation.issues 
            if issue.severity == ValidationSeverity.ERROR
        )

        execution_validation = ExecutionValidation(
            is_valid=validation.is_valid,
            warnings=warnings,
            issues=errors,
        )

        # 4. Segment Mapping
        # Elevate DraftSegment into ExecutionSegment using the immutable media asset ID
        media_asset_id = draft.execution_input.media_asset.id
        segments = tuple(
            ExecutionSegment(
                source_asset_id=media_asset_id,
                start_time=seg.start_time,
                end_time=seg.end_time,
                purpose=seg.purpose,
                tags=seg.tags,
                reasoning=seg.reasoning,
            ) for seg in draft.segments
        )

        # 5. Metadata Mapping
        # We must use deterministic timestamps to avoid generating state
        deterministic_timestamp = datetime(2000, 1, 1, tzinfo=timezone.utc)
        
        metadata = ExecutionMetadata(
            planner_version="1.0.0",
            plan_version="1.0.0",
            generated_by="DefaultExecutionComposer",
            generated_at=deterministic_timestamp,
        )

        # 6. Status Determination
        # Purely functional status determination based on validation outcome
        status = ExecutionStatus.VALIDATED if validation.is_valid else ExecutionStatus.DRAFT

        # 7. Aggregate Construction
        return ExecutionPlan(
            plan_id=plan_id,
            execution_input=draft.execution_input,
            execution_strategy=execution_strategy,
            validation=execution_validation,
            segments=segments,
            metadata=metadata,
            status=status,
        )
