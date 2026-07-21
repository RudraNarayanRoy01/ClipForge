from fastapi import APIRouter, HTTPException, Depends, status
import uuid

from src.presentation.schemas import AnalyzeVideoRequest, JobAcceptedResponse, ClipListResponse
from src.services.video_service import VideoService
from src.repositories.project_repository import ProjectRepository
from src.repositories.video_repository import VideoRepository
from src.infrastructure.ffmpeg_processor import FfmpegVideoProcessor
from src.infrastructure.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.job import Job
from src.domain.ports import IWorkflowDispatcher, IJobRepository
from src.workers.state.job_repository import global_job_repository
from src.workers.app import AsyncWorkflowDispatcher
from src.application.use_cases import GenerateClipsUseCase
from src.infrastructure.mocks import MockAudioAnalyzer, MockVisionAnalyzer, MockLLMReasoningEngine

router = APIRouter(
    prefix="/videos",
    tags=["Videos"]
)

def get_video_service(db: AsyncSession = Depends(get_db)) -> VideoService:
    video_repo = VideoRepository(db)
    project_repo = ProjectRepository(db)
    video_processor = FfmpegVideoProcessor()
    return VideoService(video_repo, project_repo, video_processor)

def get_job_repository() -> IJobRepository:
    return global_job_repository

def get_workflow_dispatcher(repo: IJobRepository = Depends(get_job_repository)) -> IWorkflowDispatcher:
    return AsyncWorkflowDispatcher(repo)

@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Video")
async def delete_video(video_id: str, service: VideoService = Depends(get_video_service)):
    """Delete a video and its physical file."""
    try:
        await service.delete_video(video_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{video_id}/clips", response_model=ClipListResponse, tags=["Clips"], summary="Get Video Clips")
async def get_clips_for_video(video_id: uuid.UUID, skip: int = 0, limit: int = 50):
    """Retrieve all AI-generated clips belonging to a specific video."""
    raise HTTPException(status_code=501, detail="Not implemented yet")

@router.post("/{video_id}/analyze", response_model=JobAcceptedResponse, status_code=202, tags=["Analysis"], summary="Trigger Multimodal Analysis")
async def analyze_video(
    video_id: uuid.UUID, 
    request: AnalyzeVideoRequest,
    db: AsyncSession = Depends(get_db),
    job_repo: IJobRepository = Depends(get_job_repository),
    dispatcher: IWorkflowDispatcher = Depends(get_workflow_dispatcher)
):
    """
    Triggers the massive multimodal AI pipeline for a video.
    Returns a Job ID immediately as this process runs in the background.
    """
    video_repo = VideoRepository(db)
    try:
        video = await video_repo.get_video(video_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Video not found")

    job = Job(name=f"analyze_video_{video_id}")
    job.accept()
    await job_repo.save(job)

    # Initialize Mock Services
    audio_analyzer = MockAudioAnalyzer()
    vision_analyzer = MockVisionAnalyzer()
    llm_engine = MockLLMReasoningEngine()
    project_repo = ProjectRepository(db)
    video_processor = FfmpegVideoProcessor()

    use_case = GenerateClipsUseCase(
        audio_analyzer=audio_analyzer,
        vision_analyzer=vision_analyzer,
        llm_engine=llm_engine,
        timeline_repo=None, # type: ignore
        project_repo=project_repo,
        video_processor=video_processor
    )

    # Dispatch to background execution
    await dispatcher.dispatch(
        job,
        use_case.execute,
        project_id=video.project_id,
        video_asset_id=video.id,
        video_path=video.file_path
    )

    return JobAcceptedResponse(
        job_id=job.id,
        message=f"Mock AI Pipeline started for {video_id} with profile {request.pipeline_profile}."
    )
