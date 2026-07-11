import json
from pydantic import BaseModel, Field
from typing import List, Optional
import typing
import dataclasses
from src.domain.ports import ICampaignIntelligence
from src.domain.campaign_entities import (
    Campaign, CampaignRules, CampaignSummary, WorthItScore,
    CampaignExecutionPlan, CampaignClipStrategy, CampaignPromptTemplate, CampaignSuitabilityAssessment
)
from src.intelligence.providers.capabilities import IStructuredOutput

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

class CampaignIntelligenceService(ICampaignIntelligence):
    def __init__(self, structured_llm: IStructuredOutput):
        self.llm = structured_llm

    async def extract_rules(self, text: str) -> CampaignRules:
        prompt = (
            "Extract the campaign rules from the following text. "
            "If a value is not explicitly stated, do not guess; leave it null/empty. "
            f"\n\nTEXT:\n{text}"
        )
        
        result_base = await self.llm.generate_object(prompt, ExtractionRulesSchema)
        result = typing.cast(ExtractionRulesSchema, result_base)
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
            f"\n\nTEXT:\n{text}"
        )
        
        result_base = await self.llm.generate_object(prompt, ExtractionSummarySchema)
        result = typing.cast(ExtractionSummarySchema, result_base)
        return CampaignSummary(
            about=result.about,
            requirements=result.requirements,
            restrictions=result.restrictions,
            deadline=result.deadline,
            payout=result.payout,
            main_risks=result.main_risks
        )

    async def calculate_worth_it_score(self, text: str, rules: CampaignRules) -> WorthItScore:
        prompt = (
            "Analyze the campaign and calculate a 'Worth-It' score out of 100 for each category. "
            "Consider the requirements, restrictions, and payout. Higher ROI is better. "
            f"\n\nRULES EXTRACTED:\n{json.dumps(rules.__dict__)}"
            f"\n\nRAW TEXT:\n{text}"
        )
        
        result_base = await self.llm.generate_object(prompt, ExtractionScoreSchema)
        result = typing.cast(ExtractionScoreSchema, result_base)
        return WorthItScore(
            estimated_roi=result.estimated_roi,
            estimated_effort=result.estimated_effort,
            campaign_complexity=result.campaign_complexity,
            submission_risk=result.submission_risk,
            overall_score=result.overall_score
        )

    async def generate_execution_plan(self, campaign: Campaign) -> CampaignExecutionPlan:
        prompt = (
            "You are a Principal Social Media Editor. Generate an Execution Plan for this campaign.\n"
            "Make deterministic decisions based on the requirements.\n"
            f"\n\nCAMPAIGN RULES:\n{json.dumps(dataclasses.asdict(campaign.rules) if campaign.rules else {})}"
            f"\n\nCAMPAIGN SUMMARY:\n{json.dumps(dataclasses.asdict(campaign.summary) if campaign.summary else {})}"
        )
        
        result_base = await self.llm.generate_object(prompt, ExecutionPlanSchema)
        result = typing.cast(ExecutionPlanSchema, result_base)
        
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
            planner_model=self.llm.__class__.__name__
        )

    async def generate_clip_strategy(self, campaign: Campaign, plan: CampaignExecutionPlan) -> CampaignClipStrategy:
        prompt = (
            "You are a Principal Social Media Editor. Generate a detailed Clip Strategy.\n"
            f"\n\nEXECUTION PLAN:\n{json.dumps(dataclasses.asdict(plan))}"
        )
        
        result_base = await self.llm.generate_object(prompt, ClipStrategySchema)
        result = typing.cast(ClipStrategySchema, result_base)
        
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

    async def generate_prompt_template(self, campaign: Campaign, plan: CampaignExecutionPlan, strategy: CampaignClipStrategy) -> CampaignPromptTemplate:
        prompt = (
            "You are a Principal Prompt Engineer. Generate the exact prompts the Video Intelligence Engine will use.\n"
            f"\n\nEXECUTION PLAN:\n{json.dumps(dataclasses.asdict(plan))}"
            f"\n\nCLIP STRATEGY:\n{json.dumps(dataclasses.asdict(strategy))}"
        )
        
        result_base = await self.llm.generate_object(prompt, PromptTemplateSchema)
        result = typing.cast(PromptTemplateSchema, result_base)
        
        return CampaignPromptTemplate(
            system_prompt=result.system_prompt,
            reasoning_prompt=result.reasoning_prompt,
            ranking_prompt=result.ranking_prompt,
            render_prompt=result.render_prompt,
            metadata_prompt=result.metadata_prompt
        )

    async def assess_suitability(self, campaign: Campaign) -> CampaignSuitabilityAssessment:
        prompt = (
            "Analyze the campaign and assess its suitability for automated video clipping.\n"
            f"\n\nCAMPAIGN RULES:\n{json.dumps(dataclasses.asdict(campaign.rules) if campaign.rules else {})}"
        )
        
        result_base = await self.llm.generate_object(prompt, SuitabilityAssessmentSchema)
        result = typing.cast(SuitabilityAssessmentSchema, result_base)
        
        return CampaignSuitabilityAssessment(
            campaign_match_score=result.campaign_match_score,
            estimated_success_probability=result.estimated_success_probability,
            missing_requirements=result.missing_requirements,
            risk_flags=result.risk_flags,
            confidence=result.confidence,
            recommendation=result.recommendation
        )
