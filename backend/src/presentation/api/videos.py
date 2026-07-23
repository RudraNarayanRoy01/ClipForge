from fastapi import APIRouter, HTTPException, Depends, status
import uuid

from src.presentation.schemas import AnalyzeVideoRequest, JobAcceptedResponse, ClipListResponse
from src.services.video_service import VideoService
from src.domain.ports import IWorkflowDispatcher, IJobRepository, IProjectRepository, IVideoRepository, IVideoProcessor, IAudioAnalyzer, IVisionAnalyzer, ILLMReasoningEngine
from src.presentation.api.campaigns import get_request_container
from src.application.use_cases import GenerateClipsUseCase
from src.domain.job import Job

router = APIRouter(
    prefix="/videos",
    tags=["Videos"]
)

def get_video_service(container = Depends(get_request_container)) -> VideoService:
    video_repo = container.resolve(IVideoRepository)
    project_repo = container.resolve(IProjectRepository)
    video_processor = container.resolve(IVideoProcessor)
    return VideoService(video_repo, project_repo, video_processor)

def get_job_repository(container = Depends(get_request_container)) -> IJobRepository:
    return container.resolve(IJobRepository)

def get_workflow_dispatcher(container = Depends(get_request_container)) -> IWorkflowDispatcher:
    return container.resolve(IWorkflowDispatcher)

def get_generate_clips_use_case(container = Depends(get_request_container)) -> GenerateClipsUseCase:
    project_repo = container.resolve(IProjectRepository)
    video_processor = container.resolve(IVideoProcessor)
    return GenerateClipsUseCase(
        audio_analyzer=container.resolve(IAudioAnalyzer),
        vision_analyzer=container.resolve(IVisionAnalyzer),
        llm_engine=container.resolve(ILLMReasoningEngine),
        timeline_repo=None, # type: ignore
        project_repo=project_repo,
        video_processor=video_processor
    )

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
    container = Depends(get_request_container),
    job_repo: IJobRepository = Depends(get_job_repository),
    dispatcher: IWorkflowDispatcher = Depends(get_workflow_dispatcher),
    use_case: GenerateClipsUseCase = Depends(get_generate_clips_use_case)
):
    """
    Triggers the massive multimodal AI pipeline for a video.
    Returns a Job ID immediately as this process runs in the background.
    """
    video_repo = container.resolve(IVideoRepository)
    try:
        video = await video_repo.get_video(video_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Video not found")

    job = Job(name=f"analyze_video_{video_id}")
    job.accept()
    await job_repo.save(job)

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
