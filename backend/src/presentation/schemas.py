from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime
import uuid

# --- COMMON ---
class HealthResponse(BaseModel):
    status: str
    message: str
    version: str
    uptime: float
    database: str
    ollama: str
    gemma: str
    whisper: str
    ffmpeg: str
    queue: str
    schema_version: str
    expected_version: str
    migration_pending: bool
    timestamp: datetime

class PaginationMeta(BaseModel):
    total_count: int
    skip: int
    limit: int

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[str] = None

class ErrorResponse(BaseModel):
    error: ErrorDetail

# --- PROJECTS ---
class ProjectCreate(BaseModel):
    name: str = Field(..., description="The name of the new clipping workspace.", json_schema_extra={"example": "My Awesome Podcast"})
    description: Optional[str] = Field(None, description="Optional description of the project.")

class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    created_at: datetime
    status: str = Field(..., json_schema_extra={"example": "active"})
    video_count: int = 0
    thumbnail_path: Optional[str] = None

class ProjectListResponse(BaseModel):
    data: List[ProjectResponse]
    meta: PaginationMeta

# --- VIDEOS ---
class LocalVideoUpload(BaseModel):
    file_path: str = Field(..., description="Absolute local path to the video file.", json_schema_extra={"example": "D:/Footage/raw_interview.mp4"})

class VideoAssetResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    file_path: str
    filename: str
    original_filename: str
    file_extension: str
    mime_type: str
    file_size_bytes: int
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    created_at: datetime

# --- CLIPS ---
class ClipResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    video_asset_id: uuid.UUID
    start_time: float
    end_time: float
    title: str = Field(..., description="AI-generated compelling title for the clip.")
    hook_text: str = Field(..., description="AI-generated engaging hook.")
    virality_score: int = Field(..., description="Score from 0-100 indicating predicted engagement.", json_schema_extra={"example": 85})
    user_approved: bool

class ClipListResponse(BaseModel):
    data: List[ClipResponse]
    meta: PaginationMeta

class ClipUpdate(BaseModel):
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    title: Optional[str] = None
    user_approved: Optional[bool] = None

# --- BACKGROUND JOBS ---
class JobAcceptedResponse(BaseModel):
    job_id: uuid.UUID
    message: str = Field(default="Task accepted and queued for processing")

class AnalyzeVideoRequest(BaseModel):
    pipeline_profile: str = Field(default="full_multimodal", description="Profile determining which ML models to run.", json_schema_extra={"example": "fast_audio_only"})
    target_length_seconds: int = Field(default=60, ge=15, le=180, description="Desired approximate length of generated clips.")

# --- CAMPAIGNS ---
class CampaignImportRequest(BaseModel):
    content_type: str = Field(..., description="Type of the campaign source (e.g., text, url, pdf)", json_schema_extra={"example": "url"})
    source: str = Field(..., description="The content or URL of the campaign", json_schema_extra={"example": "https://example.com/campaign"})
    force_import: bool = Field(default=False, description="Whether to bypass duplicate detection")

class CampaignRulesSchema(BaseModel):
    allowed_regions: List[str]
    video_duration_min: Optional[int]
    video_duration_max: Optional[int]
    aspect_ratio: Optional[str]
    resolution_requirements: Optional[str]
    caption_requirements: Optional[str]
    hashtags: List[str]
    required_audio: Optional[str]
    content_restrictions: List[str]
    rejection_reasons: List[str]
    additional_notes: Optional[str]

class CampaignSummarySchema(BaseModel):
    about: str
    requirements: str
    restrictions: str
    deadline: Optional[str]
    payout: Optional[str]
    main_risks: str

class WorthItScoreSchema(BaseModel):
    estimated_roi: int
    estimated_effort: int
    campaign_complexity: int
    submission_risk: int
    overall_score: int

class CampaignResponse(BaseModel):
    id: uuid.UUID
    title: str
    source: str
    brand: str
    campaign_url: str
    platforms: List[str]
    deadline: Optional[datetime]
    payout: str
    reward_type: str
    status: str
    confidence_score: float
    created_at: datetime
    
    rules: Optional[CampaignRulesSchema] = None
    summary: Optional[CampaignSummarySchema] = None
    worth_it_score: Optional[WorthItScoreSchema] = None

class CampaignListResponse(BaseModel):
    data: List[CampaignResponse]
    meta: PaginationMeta

class CampaignImportHistoryResponse(BaseModel):
    id: uuid.UUID
    campaign_id: Optional[uuid.UUID]
    import_timestamp: datetime
    source_type: str
    processing_status: str
    processing_duration_ms: int
    duplicate_status: str

class CampaignImportHistoryListResponse(BaseModel):
    data: List[CampaignImportHistoryResponse]
    meta: PaginationMeta

# --- PLANNING ---
class ExecutionPlanSchema(BaseModel):
    campaign_id: uuid.UUID
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
    planning_version: str
    planner_model: str
    generated_at: datetime
    planning_confidence: float
    generation_reason: str

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
    campaign_match_score: int
    estimated_success_probability: int
    missing_requirements: List[str]
    risk_flags: List[str]
    confidence: float
    recommendation: str

class PlanningResponse(BaseModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    planner_model: str
    planning_version: str
    version: int
    pipeline_status: str
    validation_status: str
    overall_confidence: float
    execution_duration_ms: int
    generated_at: datetime
    
    execution_plan: Optional[ExecutionPlanSchema] = None
    clip_strategy: Optional[ClipStrategySchema] = None
    prompt_template: Optional[PromptTemplateSchema] = None
    suitability_assessment: Optional[SuitabilityAssessmentSchema] = None

class PlanningHistoryResponse(BaseModel):
    data: List[PlanningResponse]
    meta: PaginationMeta

class PlanningRequest(BaseModel):
    force_regenerate: bool = Field(default=False, description="Force regeneration of the planning pipeline.")
