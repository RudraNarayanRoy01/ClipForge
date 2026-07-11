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

@dataclass
class CampaignImportHistory:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    campaign_id: Optional[uuid.UUID] = None
    import_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source_type: str = ""
    processing_status: str = "started"
    processing_duration_ms: int = 0
    duplicate_status: str = "none"
