from src.reasoning.execution.planner.models import ExecutionPlanDraft
from src.reasoning.execution.strategy.interfaces import IExecutionStrategy
from src.reasoning.execution.strategy.models import (
    AspectRatioStrategy,
    CTAStrategy,
    EditorialIntent,
    ExecutionStrategyResult,
    HookStrategy,
    NarrativeFlow,
    PacingProfile,
    SubtitleStrategy,
)


class DefaultExecutionStrategy(IExecutionStrategy):
    """
    Default deterministic execution strategy.
    Maps properties of the ExecutionPlanDraft to an EditorialIntent
    without relying on external state, UUIDs, or AI generation.
    """

    def generate_strategy(
        self, execution_plan_draft: ExecutionPlanDraft
    ) -> ExecutionStrategyResult:
        # Extract tags from the draft to deterministically inform the strategy
        tags = set()
        for segment in execution_plan_draft.segments:
            for tag in segment.tags:
                tags.add(tag.lower())

        # Determine Narrative Flow
        if "education" in tags or "tutorial" in tags:
            narrative_flow = NarrativeFlow.EDUCATIONAL
        elif "drama" in tags or "story" in tags:
            narrative_flow = NarrativeFlow.DRAMATIC
        elif "inspiration" in tags or "motivation" in tags:
            narrative_flow = NarrativeFlow.INSPIRATIONAL
        else:
            narrative_flow = NarrativeFlow.ENTERTAINING

        # Determine Pacing
        if "highlight" in tags or "action" in tags or "fast" in tags:
            pacing_profile = PacingProfile.FAST
        elif "slow" in tags or "atmospheric" in tags:
            pacing_profile = PacingProfile.SLOW
        else:
            pacing_profile = PacingProfile.MODERATE

        # Determine Hook and CTA
        hook_strategy = HookStrategy.STRONG_CURIOSITY
        cta_strategy = CTAStrategy.SOFT

        # Hardcode some default aspect ratio and subtitles for now
        # but could be further informed by platform target if it existed in draft
        subtitle_strategy = SubtitleStrategy.DYNAMIC_WORD_BY_WORD
        aspect_ratio_strategy = AspectRatioStrategy.VERTICAL_9_16

        # Determine transition philosophy
        if pacing_profile == PacingProfile.FAST:
            transition_philosophy = "Fast-paced hard cuts with dynamic energy"
        elif pacing_profile == PacingProfile.SLOW:
            transition_philosophy = "Smooth, deliberate crossfades"
        else:
            transition_philosophy = "Clean, seamless transitions"

        intent = EditorialIntent(
            narrative_flow=narrative_flow,
            pacing_profile=pacing_profile,
            hook_strategy=hook_strategy,
            cta_strategy=cta_strategy,
            subtitle_strategy=subtitle_strategy,
            aspect_ratio_strategy=aspect_ratio_strategy,
            transition_philosophy=transition_philosophy,
        )

        return ExecutionStrategyResult(
            execution_plan_draft=execution_plan_draft,
            editorial_intent=intent,
        )
