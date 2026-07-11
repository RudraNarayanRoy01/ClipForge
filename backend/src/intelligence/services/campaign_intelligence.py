import json
import logging
import re
from pydantic import BaseModel, Field
from typing import List, Optional, Type, TypeVar
import typing
import dataclasses
from src.domain.ports import ICampaignIntelligence
from src.domain.campaign_entities import (
    Campaign, CampaignRules, CampaignSummary, WorthItScore,
    CampaignExecutionPlan, CampaignClipStrategy, CampaignPromptTemplate, CampaignSuitabilityAssessment,
    PlanningValidationError, PlanningConfidenceError, PlanningGenerationError, PromptSanitizationError
)
from src.intelligence.providers.capabilities import IStructuredOutput

logger = logging.getLogger(__name__)

# Constants
MIN_EXECUTION_CONFIDENCE = 0.70
MIN_SUITABILITY_CONFIDENCE = 0.65
PLANNING_VERSION = "1.1.0"
MAX_PROMPT_LENGTH = 50000

# Schemas remain exactly the same
class ExtractionRulesSchema(BaseModel):
    allowed_regions: List[str] = Field(default_factory=list)
    video_duration_min: Optional[int] = None
    video_duration_max: Optional[int] = None
    aspect_ratio: Optional[str] = None
    resolution_requirements: Optional[str] = None
    caption_requirements: Optional[str] = None
    hashtags: List[str] = Field(default_factory=list)
    required_audio: Optional[str] = None
    content_restrictions: List[str] = Field(default_factory=list)
    rejection_reasons: List[str] = Field(default_factory=list)
    additional_notes: Optional[str] = None

class ExtractionSummarySchema(BaseModel):
    about: str = Field(..., description="What the campaign is about")
    requirements: str = Field(..., description="What must be done")
    restrictions: str = Field(..., description="Important restrictions")
    deadline: Optional[str] = None
    payout: Optional[str] = None
    main_risks: str = Field(..., description="Main risks")

class ExtractionScoreSchema(BaseModel):
    estimated_roi: int = Field(..., ge=0, le=100)
    estimated_effort: int = Field(..., ge=0, le=100)
    campaign_complexity: int = Field(..., ge=0, le=100)
    submission_risk: int = Field(..., ge=0, le=100)
    overall_score: int = Field(..., ge=0, le=100)

class ExecutionPlanSchema(BaseModel):
    target_platform: str
    recommended_clip_length: int
    minimum_clip_length: int
    maximum_clip_length: int
    preferred_hook_style: str
    preferred_editing_style: str
    caption_style: str
    call_to_action: str
    crop_strategy: str
    subtitle_style: str
    required_emotions: List[str]
    required_topics: List[str]
    priority_scene_types: List[str]
    required_audio_style: str
    brand_voice: str
    virality_focus: str
    estimated_clip_count: int
    estimated_editing_time_minutes: int
    confidence_score: float

class ClipStrategySchema(BaseModel):
    hook_priorities: List[str]
    scene_priorities: List[str]
    speech_characteristics: List[str]
    emotion_targets: List[str]
    energy_targets: List[str]
    pacing: str
    transition_style: str
    camera_motion_preference: str
    visual_focus: str
    audio_focus: str

class PromptTemplateSchema(BaseModel):
    system_prompt: str
    reasoning_prompt: str
    ranking_prompt: str
    render_prompt: str
    metadata_prompt: str

class SuitabilityAssessmentSchema(BaseModel):
    campaign_match_score: int = Field(..., ge=0, le=100)
    estimated_success_probability: int = Field(..., ge=0, le=100)
    missing_requirements: List[str]
    risk_flags: List[str]
    confidence: float
    recommendation: str

T = TypeVar("T", bound=BaseModel)

class CampaignIntelligenceService(ICampaignIntelligence):
    def __init__(self, structured_llm: IStructuredOutput):
        self.llm = structured_llm

    def _sanitize_text(self, text: str) -> str:
        """Sanitizes prompt text to prevent obvious injection and control char issues."""
        if not text:
            return ""
        # Remove dangerous control characters (keep tabs, newlines, carriage returns)
        sanitized = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)
        
        # Prevent very basic prompt injection phrases
        lower_text = sanitized.lower()
        if "ignore previous instructions" in lower_text or "system override" in lower_text:
            raise PromptSanitizationError("Detected potential prompt injection attempt.")
            
        # Limit length
        if len(sanitized) > MAX_PROMPT_LENGTH:
            sanitized = sanitized[:MAX_PROMPT_LENGTH] + "\n...[TRUNCATED]"
            
        return sanitized

    async def _generate_with_retry(self, prompt: str, schema: Type[T], max_retries: int = 3) -> T:
        import time
        attempt = 0
        last_exception = None
        while attempt < max_retries:
            attempt += 1
            start_time = time.time()
            try:
                result_base = await self.llm.generate_object(prompt, schema)
                duration = time.time() - start_time
                logger.info(
                    "LLM Generation successful",
                    extra={
                        "planner_model": self.llm.__class__.__name__,
                        "planning_version": PLANNING_VERSION,
                        "generation_duration_sec": round(duration, 2),
                        "attempt": attempt,
                        "schema": schema.__name__
                    }
                )
                return typing.cast(T, result_base)
            except Exception as e:
                duration = time.time() - start_time
                last_exception = e
                logger.warning(
                    f"LLM Generation failed on attempt {attempt}: {e}",
                    extra={
                        "planner_model": self.llm.__class__.__name__,
                        "planning_version": PLANNING_VERSION,
                        "generation_duration_sec": round(duration, 2),
                        "attempt": attempt,
                        "schema": schema.__name__
                    }
                )
                # Retry transient LLM failures.
        
        logger.error(f"Exhausted {max_retries} retries for {schema.__name__}")
        raise PlanningGenerationError(f"Failed to generate {schema.__name__} after {max_retries} attempts. Last error: {last_exception}")

    # --- Builders ---
    def _build_execution_plan_prompt(self, campaign: Campaign) -> str:
        rules_text = json.dumps(dataclasses.asdict(campaign.rules)) if campaign.rules else "{}"
        summary_text = json.dumps(dataclasses.asdict(campaign.summary)) if campaign.summary else "{}"
        return (
            "You are a Principal Social Media Editor. Generate an Execution Plan for this campaign.\n"
            "Make deterministic decisions based on the requirements.\n"
            f"\n\nCAMPAIGN RULES:\n{self._sanitize_text(rules_text)}"
            f"\n\nCAMPAIGN SUMMARY:\n{self._sanitize_text(summary_text)}"
        )

    def _build_clip_strategy_prompt(self, plan: CampaignExecutionPlan) -> str:
        plan_text = json.dumps(dataclasses.asdict(plan))
        return (
            "You are a Principal Social Media Editor. Generate a detailed Clip Strategy.\n"
            f"\n\nEXECUTION PLAN:\n{plan_text}"
        )

    def _build_prompt_template_prompt(self, plan: CampaignExecutionPlan, strategy: CampaignClipStrategy) -> str:
        plan_text = json.dumps(dataclasses.asdict(plan))
        strategy_text = json.dumps(dataclasses.asdict(strategy))
        return (
            "You are a Principal Prompt Engineer. Generate the exact prompts the Video Intelligence Engine will use.\n"
            f"\n\nEXECUTION PLAN:\n{plan_text}"
            f"\n\nCLIP STRATEGY:\n{strategy_text}"
        )

    def _build_suitability_prompt(self, campaign: Campaign) -> str:
        rules_text = json.dumps(dataclasses.asdict(campaign.rules)) if campaign.rules else "{}"
        return (
            "Analyze the campaign and assess its suitability for automated video clipping.\n"
            f"\n\nCAMPAIGN RULES:\n{self._sanitize_text(rules_text)}"
        )

    # --- Legacy methods from previous batches ---
    async def extract_rules(self, text: str) -> CampaignRules:
        prompt = (
            "Extract the campaign rules from the following text. "
            "If a value is not explicitly stated, do not guess; leave it null/empty. "
            f"\n\nTEXT:\n{self._sanitize_text(text)}"
        )
        result = await self._generate_with_retry(prompt, ExtractionRulesSchema)
        return CampaignRules(
            allowed_regions=result.allowed_regions,
            video_duration_min=result.video_duration_min,
            video_duration_max=result.video_duration_max,
            aspect_ratio=result.aspect_ratio,
            resolution_requirements=result.resolution_requirements,
            caption_requirements=result.caption_requirements,
            hashtags=result.hashtags,
            required_audio=result.required_audio,
            content_restrictions=result.content_restrictions,
            rejection_reasons=result.rejection_reasons,
            additional_notes=result.additional_notes
        )

    async def generate_summary(self, text: str) -> CampaignSummary:
        prompt = (
            "Generate a concise campaign summary from the following text. "
            "Focus on the main objectives, rules, and risks. "
            f"\n\nTEXT:\n{self._sanitize_text(text)}"
        )
        result = await self._generate_with_retry(prompt, ExtractionSummarySchema)
        return CampaignSummary(
            about=result.about,
            requirements=result.requirements,
            restrictions=result.restrictions,
            deadline=result.deadline,
            payout=result.payout,
            main_risks=result.main_risks
        )

    async def calculate_worth_it_score(self, text: str, rules: CampaignRules) -> WorthItScore:
        rules_str = json.dumps(dataclasses.asdict(rules))
        prompt = (
            "Analyze the campaign and calculate a 'Worth-It' score out of 100 for each category. "
            "Consider the requirements, restrictions, and payout. Higher ROI is better. "
            f"\n\nRULES EXTRACTED:\n{rules_str}"
            f"\n\nRAW TEXT:\n{self._sanitize_text(text)}"
        )
        result = await self._generate_with_retry(prompt, ExtractionScoreSchema)
        return WorthItScore(
            estimated_roi=result.estimated_roi,
            estimated_effort=result.estimated_effort,
            campaign_complexity=result.campaign_complexity,
            submission_risk=result.submission_risk,
            overall_score=result.overall_score
        )

    # --- Hardened Planning Methods ---
    def _validate_execution_plan(self, result: ExecutionPlanSchema) -> None:
        if not (result.minimum_clip_length <= result.recommended_clip_length <= result.maximum_clip_length):
            raise PlanningValidationError("Clip length bounds are illogical: min <= recommended <= max violated.")
        if result.estimated_clip_count <= 0:
            raise PlanningValidationError("estimated_clip_count must be > 0.")
        if result.estimated_editing_time_minutes < 0:
            raise PlanningValidationError("estimated_editing_time_minutes cannot be negative.")
        if not (0.0 <= result.confidence_score <= 1.0):
            raise PlanningValidationError("confidence_score must be between 0.0 and 1.0")
            
        if result.confidence_score < MIN_EXECUTION_CONFIDENCE:
            raise PlanningConfidenceError(
                message=f"Execution plan confidence {result.confidence_score} is below threshold {MIN_EXECUTION_CONFIDENCE}",
                confidence=result.confidence_score,
                planner_model=self.llm.__class__.__name__,
                planning_version=PLANNING_VERSION
            )

    async def generate_execution_plan(self, campaign: Campaign) -> CampaignExecutionPlan:
        prompt = self._build_execution_plan_prompt(campaign)
        result = await self._generate_with_retry(prompt, ExecutionPlanSchema)
        self._validate_execution_plan(result)
        
        return CampaignExecutionPlan(
            campaign_id=campaign.id,
            target_platform=result.target_platform,
            recommended_clip_length=result.recommended_clip_length,
            minimum_clip_length=result.minimum_clip_length,
            maximum_clip_length=result.maximum_clip_length,
            preferred_hook_style=result.preferred_hook_style,
            preferred_editing_style=result.preferred_editing_style,
            caption_style=result.caption_style,
            call_to_action=result.call_to_action,
            crop_strategy=result.crop_strategy,
            subtitle_style=result.subtitle_style,
            required_emotions=result.required_emotions,
            required_topics=result.required_topics,
            priority_scene_types=result.priority_scene_types,
            required_audio_style=result.required_audio_style,
            brand_voice=result.brand_voice,
            virality_focus=result.virality_focus,
            estimated_clip_count=result.estimated_clip_count,
            estimated_editing_time_minutes=result.estimated_editing_time_minutes,
            confidence_score=result.confidence_score,
            planning_version=PLANNING_VERSION,
            planner_model=self.llm.__class__.__name__,
            planning_confidence=result.confidence_score,
            generation_reason="automated_planning_engine"
        )

    def _validate_clip_strategy(self, result: ClipStrategySchema) -> None:
        if not result.hook_priorities:
            raise PlanningValidationError("hook_priorities cannot be empty.")
        if not result.scene_priorities:
            raise PlanningValidationError("scene_priorities cannot be empty.")

    async def generate_clip_strategy(self, campaign: Campaign, plan: CampaignExecutionPlan) -> CampaignClipStrategy:
        prompt = self._build_clip_strategy_prompt(plan)
        result = await self._generate_with_retry(prompt, ClipStrategySchema)
        self._validate_clip_strategy(result)
        
        return CampaignClipStrategy(
            hook_priorities=result.hook_priorities,
            scene_priorities=result.scene_priorities,
            speech_characteristics=result.speech_characteristics,
            emotion_targets=result.emotion_targets,
            energy_targets=result.energy_targets,
            pacing=result.pacing,
            transition_style=result.transition_style,
            camera_motion_preference=result.camera_motion_preference,
            visual_focus=result.visual_focus,
            audio_focus=result.audio_focus
        )

    def _validate_prompt_template(self, result: PromptTemplateSchema) -> None:
        if not result.system_prompt or not result.reasoning_prompt:
            raise PlanningValidationError("Prompt templates cannot have empty system or reasoning prompts.")

    async def generate_prompt_template(self, campaign: Campaign, plan: CampaignExecutionPlan, strategy: CampaignClipStrategy) -> CampaignPromptTemplate:
        prompt = self._build_prompt_template_prompt(plan, strategy)
        result = await self._generate_with_retry(prompt, PromptTemplateSchema)
        self._validate_prompt_template(result)
        
        return CampaignPromptTemplate(
            system_prompt=result.system_prompt,
            reasoning_prompt=result.reasoning_prompt,
            ranking_prompt=result.ranking_prompt,
            render_prompt=result.render_prompt,
            metadata_prompt=result.metadata_prompt
        )

    def _validate_suitability_assessment(self, result: SuitabilityAssessmentSchema) -> None:
        if not (0 <= result.campaign_match_score <= 100):
            raise PlanningValidationError("campaign_match_score must be between 0 and 100")
        if not (0 <= result.estimated_success_probability <= 100):
            raise PlanningValidationError("estimated_success_probability must be between 0 and 100")
            
        if result.confidence < MIN_SUITABILITY_CONFIDENCE:
            raise PlanningConfidenceError(
                message=f"Suitability confidence {result.confidence} is below threshold {MIN_SUITABILITY_CONFIDENCE}",
                confidence=result.confidence,
                planner_model=self.llm.__class__.__name__,
                planning_version=PLANNING_VERSION
            )

    async def assess_suitability(self, campaign: Campaign) -> CampaignSuitabilityAssessment:
        prompt = self._build_suitability_prompt(campaign)
        result = await self._generate_with_retry(prompt, SuitabilityAssessmentSchema)
        self._validate_suitability_assessment(result)
        
        return CampaignSuitabilityAssessment(
            campaign_match_score=result.campaign_match_score,
            estimated_success_probability=result.estimated_success_probability,
            missing_requirements=result.missing_requirements,
            risk_flags=result.risk_flags,
            confidence=result.confidence,
            recommendation=result.recommendation
        )
