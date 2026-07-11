import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Any
from datetime import datetime, timezone

@dataclass(frozen=True)
class WorthItScore:
    estimated_roi: int  # 0-100
    estimated_effort: int  # 0-100
    campaign_complexity: int  # 0-100
    submission_risk: int  # 0-100
    overall_score: int  # 0-100

@dataclass(frozen=True)
class CampaignRules:
    allowed_regions: List[str] = field(default_factory=list)
    video_duration_min: Optional[int] = None
    video_duration_max: Optional[int] = None
    aspect_ratio: Optional[str] = None
    resolution_requirements: Optional[str] = None
    caption_requirements: Optional[str] = None
    hashtags: List[str] = field(default_factory=list)
    required_audio: Optional[str] = None
    content_restrictions: List[str] = field(default_factory=list)
    rejection_reasons: List[str] = field(default_factory=list)
    additional_notes: Optional[str] = None

@dataclass(frozen=True)
class CampaignSummary:
    about: str
    requirements: str
    restrictions: str
    main_risks: str
    deadline: Optional[str] = None
    payout: Optional[str] = None

@dataclass(frozen=True)
class CampaignExecutionPlan:
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
    planning_version: str = "1.0.0"
    planner_model: str = "unknown"
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    planning_confidence: float = 0.0
    generation_reason: str = "initial_planning"

@dataclass(frozen=True)
class CampaignClipStrategy:
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

@dataclass(frozen=True)
class CampaignPromptTemplate:
    system_prompt: str
    reasoning_prompt: str
    ranking_prompt: str
    render_prompt: str
    metadata_prompt: str

@dataclass(frozen=True)
class CampaignSuitabilityAssessment:
    campaign_match_score: int
    estimated_success_probability: int
    missing_requirements: List[str]
    risk_flags: List[str]
    confidence: float
    recommendation: str

from enum import Enum

class CampaignStatus(str, Enum):
    IMPORTED = "imported"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    ARCHIVED = "archived"

@dataclass
class Campaign:
    """Aggregate Root for a Campaign"""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    title: str = "Untitled Campaign"
    source: str = ""
    brand: str = ""
    campaign_url: str = ""
    platforms: List[str] = field(default_factory=list)
    deadline: Optional[datetime] = None
    payout: str = ""
    reward_type: str = ""
    
    rules: Optional[CampaignRules] = None
    summary: Optional[CampaignSummary] = None
    worth_it_score: Optional[WorthItScore] = None
    execution_plan: Optional[CampaignExecutionPlan] = None
    clip_strategy: Optional[CampaignClipStrategy] = None
    prompt_template: Optional[CampaignPromptTemplate] = None
    suitability_assessment: Optional[CampaignSuitabilityAssessment] = None
    
    # Raw extracted content, kept separate from normalized rules
    raw_content: str = ""
    confidence_score: float = 0.0
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: CampaignStatus = CampaignStatus.IMPORTED

class CampaignNotFoundError(Exception):
    """Raised when a campaign cannot be found in the repository."""
    def __init__(self, campaign_id: str):
        super().__init__(f"Campaign {campaign_id} not found")
        self.campaign_id = campaign_id

class DuplicateCampaignError(Exception):
    """Raised when a campaign is determined to be a duplicate."""
    def __init__(self, duplicate_id: str, reason: str):
        super().__init__(f"Duplicate campaign detected (ID: {duplicate_id}): {reason}")
        self.duplicate_id = duplicate_id
        self.reason = reason

class PlanningValidationError(Exception):
    """Raised when AI-generated planning output fails business rule validation."""
    pass

class PlanningConfidenceError(Exception):
    """Raised when the AI planner's confidence score is below the required threshold."""
    def __init__(self, message: str, confidence: float, planner_model: str, planning_version: str):
        super().__init__(message)
        self.confidence = confidence
        self.planner_model = planner_model
        self.planning_version = planning_version

class PlanningGenerationError(Exception):
    """Raised when the AI planner fails to generate a valid plan after maximum retries."""
    pass

class PromptSanitizationError(Exception):
    """Raised when the prompt contains dangerous control characters or severe injection attempts."""
    pass

@dataclass
class CampaignImportHistory:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    campaign_id: Optional[uuid.UUID] = None
    import_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source_type: str = ""
    processing_status: str = "started"
    processing_duration_ms: int = 0
    duplicate_status: str = "none"
