import json
from pydantic import BaseModel, Field
from typing import List, Optional
import typing
from src.domain.ports import ICampaignIntelligence
from src.domain.campaign_entities import CampaignRules, CampaignSummary, WorthItScore
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
