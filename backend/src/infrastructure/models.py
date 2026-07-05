import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, JSON
from typing import Any
from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

class ProjectModel(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    status: Mapped[str] = mapped_column(String, default="created")
    
    videos: Mapped[list["VideoAssetModel"]] = relationship("VideoAssetModel", back_populates="project", cascade="all, delete")
    clips: Mapped[list["ClipSegmentModel"]] = relationship("ClipSegmentModel", back_populates="project", cascade="all, delete")

class VideoAssetModel(Base):
    __tablename__ = "video_assets"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String, ForeignKey("projects.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)
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
