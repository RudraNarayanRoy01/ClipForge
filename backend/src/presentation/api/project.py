from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
import uuid
from typing import List

from ..schemas import ProjectCreate, ProjectResponse, ProjectListResponse, VideoAssetResponse
from ...services.project_service import ProjectService
from ...services.video_service import VideoService
from ...repositories.project_repository import ProjectRepository
from ...repositories.video_repository import VideoRepository
from ...infrastructure.ffmpeg_processor import FfmpegVideoProcessor
from ...infrastructure.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    repo = ProjectRepository(db)
    return ProjectService(repo)

def get_video_service(db: AsyncSession = Depends(get_db)) -> VideoService:
    video_repo = VideoRepository(db)
    project_repo = ProjectRepository(db)
    video_processor = FfmpegVideoProcessor()
    return VideoService(video_repo, project_repo, video_processor)

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED, summary="Create Workspace")
async def create_project(project: ProjectCreate, service: ProjectService = Depends(get_project_service)):
    """Create a new video clipping project workspace."""
    new_project = await service.create_project(project)
    return new_project

@router.get("/", response_model=ProjectListResponse, summary="List Workspaces")
async def list_projects(skip: int = 0, limit: int = 50, service: ProjectService = Depends(get_project_service)):
    """List all projects with pagination."""
    return await service.list_projects(skip=skip, limit=limit)

@router.get("/{project_id}", response_model=ProjectResponse, summary="Get Workspace Details")
async def get_project(project_id: str, service: ProjectService = Depends(get_project_service)):
    """Get complete workspace details by its ID."""
    return await service.get_project(project_id)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Workspace")
async def delete_project(project_id: str, service: ProjectService = Depends(get_project_service)):
    """Delete a workspace and all its data."""
    await service.delete_project(project_id)

@router.post("/{project_id}/videos", response_model=VideoAssetResponse, summary="Upload Video")
async def upload_video(project_id: str, file: UploadFile = File(...), service: VideoService = Depends(get_video_service)):
    """Upload a new video to the project workspace."""
    return await service.upload_video(project_id, file)

@router.get("/{project_id}/videos", response_model=List[VideoAssetResponse], summary="List Videos")
async def list_videos(project_id: str, service: VideoService = Depends(get_video_service)):
    """List all videos imported into the project."""
    return await service.list_videos(project_id)
