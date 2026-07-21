import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
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


class ExecutionStatus(str, Enum):
    CREATED = "created"
    INITIALIZED = "initialized"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PipelineStatus(str, Enum):
    NOT_STARTED = "not_started"
    RUNNING = "running"
    EXECUTION_PLAN_COMPLETE = "execution_plan_complete"
    CLIP_STRATEGY_COMPLETE = "clip_strategy_complete"
    PROMPT_TEMPLATE_COMPLETE = "prompt_template_complete"
    SUITABILITY_COMPLETE = "suitability_complete"
    COMPLETED = "completed"
    FAILED = "failed"

class ValidationStatus(str, Enum):
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"

@dataclass
class PlanningPipelineResult:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    campaign_id: uuid.UUID = field(default_factory=uuid.uuid4)
    planner_model: str = "unknown"
    planning_version: str = "1.0.0"
    version: int = 1
    
    # Domain-specific progress
    pipeline_status: PipelineStatus = PipelineStatus.NOT_STARTED
    validation_status: ValidationStatus = ValidationStatus.PENDING
    overall_confidence: float = 0.0
    execution_duration_ms: int = 0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Generic Execution Lifecycle
    execution_status: ExecutionStatus = ExecutionStatus.CREATED
    previous_execution_status: Optional[ExecutionStatus] = None
    execution_status_updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    execution_plan: Optional[CampaignExecutionPlan] = None
    clip_strategy: Optional[CampaignClipStrategy] = None
    prompt_template: Optional[CampaignPromptTemplate] = None
    suitability_assessment: Optional[CampaignSuitabilityAssessment] = None

    def transition_execution_state(self, new_status: ExecutionStatus) -> None:
        """Deterministic state transition for generic pipeline execution lifecycle."""
        # Enforce basic invariant: cannot transition if already in a terminal state unless resetting
        terminal_states = {ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED}
        if self.execution_status in terminal_states and new_status not in {ExecutionStatus.CREATED, ExecutionStatus.INITIALIZED}:
             raise ValueError(f"Cannot transition pipeline execution from terminal state {self.execution_status} to {new_status}")
             
        self.previous_execution_status = self.execution_status
        self.execution_status = new_status
        self.execution_status_updated_at = datetime.now(timezone.utc)

    def validate_consistency(self) -> None:
        """
        Ensures the pipeline result state is internally consistent.
        Rejects invalid combinations of status and data.
        """
        if self.pipeline_status in (PipelineStatus.COMPLETED, PipelineStatus.EXECUTION_PLAN_COMPLETE) and not self.execution_plan:
            from src.domain.errors import ValidationError
            raise ValidationError("Execution plan is missing but status implies it is complete.")
            
        if self.pipeline_status in (PipelineStatus.COMPLETED, PipelineStatus.CLIP_STRATEGY_COMPLETE) and not self.clip_strategy:
            from src.domain.errors import ValidationError
            raise ValidationError("Clip strategy is missing but status implies it is complete.")
            
        if self.pipeline_status in (PipelineStatus.COMPLETED, PipelineStatus.PROMPT_TEMPLATE_COMPLETE) and not self.prompt_template:
            from src.domain.errors import ValidationError
            raise ValidationError("Prompt template is missing but status implies it is complete.")
            
        if self.pipeline_status in (PipelineStatus.COMPLETED, PipelineStatus.SUITABILITY_COMPLETE) and not self.suitability_assessment:
            from src.domain.errors import ValidationError
            raise ValidationError("Suitability assessment is missing but status implies it is complete.")

    def compute_overall_confidence(self) -> None:
        """
        Deterministically aggregates overall confidence based on execution_plan and suitability_assessment.
        If either is missing, defaults to 0.0 or the available one.
        """
        confidences = []
        if self.execution_plan and hasattr(self.execution_plan, 'confidence_score'):
            confidences.append(self.execution_plan.confidence_score)
        if self.suitability_assessment and hasattr(self.suitability_assessment, 'confidence'):
            confidences.append(self.suitability_assessment.confidence)
            
        if confidences:
            self.overall_confidence = sum(confidences) / len(confidences)
        else:
            self.overall_confidence = 0.0


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
