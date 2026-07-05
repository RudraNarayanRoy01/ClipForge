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

class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    status: str = Field(..., json_schema_extra={"example": "active"})

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
    duration: float = Field(..., description="Duration of the video in seconds.")
    resolution: Dict[str, int] = Field(..., json_schema_extra={"example": {"width": 1920, "height": 1080}})
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
