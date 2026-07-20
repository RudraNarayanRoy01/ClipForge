from dataclasses import dataclass
from enum import Enum

from src.reasoning.execution.planner.models import ExecutionPlanDraft


class NarrativeFlow(Enum):
    EDUCATIONAL = "EDUCATIONAL"
    ENTERTAINING = "ENTERTAINING"
    INSPIRATIONAL = "INSPIRATIONAL"
    DRAMATIC = "DRAMATIC"


class PacingProfile(Enum):
    FAST = "FAST"
    MODERATE = "MODERATE"
    SLOW = "SLOW"
    DYNAMIC = "DYNAMIC"


class HookStrategy(Enum):
    STRONG_CURIOSITY = "STRONG_CURIOSITY"
    DIRECT_ACTION = "DIRECT_ACTION"
    EMOTIONAL_RESONANCE = "EMOTIONAL_RESONANCE"
    SOFT_INTRO = "SOFT_INTRO"


class CTAStrategy(Enum):
    SOFT = "SOFT"
    DIRECT = "DIRECT"
    URGENT = "URGENT"
    NONE = "NONE"


class SubtitleStrategy(Enum):
    DYNAMIC_WORD_BY_WORD = "DYNAMIC_WORD_BY_WORD"
    STATIC_SENTENCE = "STATIC_SENTENCE"
    MINIMALIST = "MINIMALIST"
    NONE = "NONE"


class AspectRatioStrategy(Enum):
    VERTICAL_9_16 = "VERTICAL_9_16"
    SQUARE_1_1 = "SQUARE_1_1"
    WIDESCREEN_16_9 = "WIDESCREEN_16_9"


@dataclass(frozen=True)
class EditorialIntent:
    """
    Represents the editorial intent of the execution strategy.
    Does not contain implementation instructions.
    """
    narrative_flow: NarrativeFlow
    pacing_profile: PacingProfile
    hook_strategy: HookStrategy
    cta_strategy: CTAStrategy
    subtitle_strategy: SubtitleStrategy
    aspect_ratio_strategy: AspectRatioStrategy
    transition_philosophy: str


@dataclass(frozen=True)
class ExecutionStrategyResult:
    """
    Represents the deterministic output of the Execution Strategy Engine.
    Combines the ExecutionPlanDraft with the generated EditorialIntent.
    """
    execution_plan_draft: ExecutionPlanDraft
    editorial_intent: EditorialIntent
