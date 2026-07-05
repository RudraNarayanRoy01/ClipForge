from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
import uuid

from ..schemas import AnalyzeVideoRequest, JobAcceptedResponse, ClipListResponse
from ...services.video_service import VideoService
from ...repositories.project_repository import ProjectRepository
from ...repositories.video_repository import VideoRepository
from ...infrastructure.ffmpeg_processor import FfmpegVideoProcessor
from ...infrastructure.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/videos",
    tags=["Videos"]
)

def get_video_service(db: AsyncSession = Depends(get_db)) -> VideoService:
    video_repo = VideoRepository(db)
    project_repo = ProjectRepository(db)
    video_processor = FfmpegVideoProcessor()
    return VideoService(video_repo, project_repo, video_processor)

@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Video")
async def delete_video(video_id: str, service: VideoService = Depends(get_video_service)):
    """Delete a video and its physical file."""
    await service.delete_video(video_id)

@router.get("/{video_id}/clips", response_model=ClipListResponse, tags=["Clips"], summary="Get Video Clips")
async def get_clips_for_video(video_id: uuid.UUID, skip: int = 0, limit: int = 50):
    """Retrieve all AI-generated clips belonging to a specific video."""
    raise HTTPException(status_code=501, detail="Not implemented yet")

@router.post("/{video_id}/analyze", response_model=JobAcceptedResponse, status_code=202, tags=["Analysis"], summary="Trigger Multimodal Analysis")
async def analyze_video(video_id: uuid.UUID, request: AnalyzeVideoRequest):
    """
    Triggers the massive multimodal AI pipeline for a video.
    Returns a Job ID immediately as this process runs in the background.
    
    In Milestone 2, this will inject the Mock dependencies and execute the Use Case.
    """
    return JobAcceptedResponse(
        job_id=uuid.uuid4(),
        message=f"Mock AI Pipeline started for {video_id} with profile {request.pipeline_profile}."
    )
