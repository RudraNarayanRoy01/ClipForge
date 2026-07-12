import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from typing import Any
from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database import Base
from src.domain.campaign_entities import CampaignStatus, PipelineStatus, ValidationStatus

class ProjectModel(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    storage_path: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="EMPTY")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    video_count: Mapped[int] = mapped_column(Integer, default=0)
    thumbnail_path: Mapped[str | None] = mapped_column(String, nullable=True)

    videos: Mapped[list["VideoAssetModel"]] = relationship("VideoAssetModel", back_populates="project", cascade="all, delete")
    clips: Mapped[list["ClipSegmentModel"]] = relationship("ClipSegmentModel", back_populates="project", cascade="all, delete")

class VideoAssetModel(Base):
    __tablename__ = "video_assets"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String, ForeignKey("projects.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    filename: Mapped[str] = mapped_column(String, default="")
    original_filename: Mapped[str] = mapped_column(String, default="")
    file_extension: Mapped[str] = mapped_column(String, default="")
    mime_type: Mapped[str] = mapped_column(String, default="")
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    duration: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fps: Mapped[float | None] = mapped_column(Float, nullable=True)
    storage_path: Mapped[str] = mapped_column(String, default="")
    resolution_w: Mapped[int] = mapped_column(Integer, default=1920)
    resolution_h: Mapped[int] = mapped_column(Integer, default=1080)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    project: Mapped["ProjectModel"] = relationship("ProjectModel", back_populates="videos")
    timeline_context: Mapped["TimelineContextModel"] = relationship("TimelineContextModel", back_populates="video", uselist=False, cascade="all, delete")

class ClipSegmentModel(Base):
    __tablename__ = "clip_segments"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String, ForeignKey("projects.id"), nullable=False)
    video_asset_id: Mapped[str] = mapped_column(String, ForeignKey("video_assets.id"), nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    title: Mapped[str] = mapped_column(String, default="")
    hook_text: Mapped[str] = mapped_column(String, default="")
    hashtags: Mapped[list[str]] = mapped_column(JSON, default=list)  # JSON array
    captions: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)  # JSON array of GeneratedCaption
    thumbnail_timestamp: Mapped[float] = mapped_column(Float, default=0.0)
    virality_score: Mapped[int] = mapped_column(Integer, default=0)
    ai_rationale: Mapped[str] = mapped_column(String, default="")
    user_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    
    project: Mapped["ProjectModel"] = relationship("ProjectModel", back_populates="clips")

class TimelineContextModel(Base):
    __tablename__ = "timeline_contexts"
    
    # We use the video_asset_id as the primary key since it's a 1:1 relationship
    video_asset_id: Mapped[str] = mapped_column(String, ForeignKey("video_assets.id"), primary_key=True)
    
    # Store the massive matrix as JSON blobs to avoid millions of rows in SQLite
    words_json: Mapped[list] = mapped_column(JSON, default=list)
    speakers_json: Mapped[list] = mapped_column(JSON, default=list)
    energy_json: Mapped[list] = mapped_column(JSON, default=list)
    silences_json: Mapped[list] = mapped_column(JSON, default=list)
    scenes_json: Mapped[list] = mapped_column(JSON, default=list)
    faces_json: Mapped[list] = mapped_column(JSON, default=list)
    emotions_json: Mapped[list] = mapped_column(JSON, default=list)
    gestures_json: Mapped[list] = mapped_column(JSON, default=list)
    objects_json: Mapped[list] = mapped_column(JSON, default=list)
    ocr_texts_json: Mapped[list] = mapped_column(JSON, default=list)
    topics_json: Mapped[list] = mapped_column(JSON, default=list)
    
    video: Mapped["VideoAssetModel"] = relationship("VideoAssetModel", back_populates="timeline_context")

class CampaignModel(Base):
    __tablename__ = "campaigns"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String, default="Untitled Campaign")
    source: Mapped[str] = mapped_column(String, default="")
    brand: Mapped[str] = mapped_column(String, default="")
    campaign_url: Mapped[str] = mapped_column(String, default="")
    platforms: Mapped[list[str]] = mapped_column(JSON, default=list)
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    payout: Mapped[str] = mapped_column(String, default="")
    reward_type: Mapped[str] = mapped_column(String, default="")
    
    rules_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    summary_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    worth_it_score_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    execution_plan_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    clip_strategy_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    prompt_template_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    suitability_assessment_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    raw_content: Mapped[str] = mapped_column(String, default="")
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    status: Mapped[CampaignStatus] = mapped_column(SQLEnum(CampaignStatus), default=CampaignStatus.IMPORTED)

class CampaignImportHistoryModel(Base):
    __tablename__ = "campaign_import_history"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id: Mapped[str | None] = mapped_column(String, ForeignKey("campaigns.id"), nullable=True)
    import_timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    source_type: Mapped[str] = mapped_column(String, default="")
    processing_status: Mapped[str] = mapped_column(String, default="started")
    processing_duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_status: Mapped[str] = mapped_column(String, default="none")

class PlanningPipelineResultModel(Base):
    __tablename__ = "planning_pipeline_results"
    
    # We use campaign_id as primary key to ensure one result per campaign (1:1)
    campaign_id: Mapped[str] = mapped_column(String, ForeignKey("campaigns.id"), primary_key=True)
    planner_model: Mapped[str] = mapped_column(String, default="")
    planning_version: Mapped[str] = mapped_column(String, default="")
    pipeline_status: Mapped[PipelineStatus] = mapped_column(SQLEnum(PipelineStatus), default=PipelineStatus.NOT_STARTED)
    validation_status: Mapped[ValidationStatus] = mapped_column(SQLEnum(ValidationStatus), default=ValidationStatus.PENDING)
    overall_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    execution_duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    execution_plan_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    clip_strategy_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    prompt_template_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    suitability_assessment_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
