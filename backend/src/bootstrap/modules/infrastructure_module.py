import httpx
from src.infrastructure.di.container import Container
from src.bootstrap.modules import DIModule
from src.config.system_settings import SystemSettings
from src.infrastructure.database import get_db, AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.ports import IJobRepository, IProjectRepository, IWorkflowDispatcher, IVideoProcessor, IVideoRepository
from src.repositories.job_repository import JobRepository
from src.repositories.project_repository import ProjectRepository
from src.repositories.video_repository import VideoRepository
from src.workers.app import ApiSafeAsyncWorkflowDispatcher
from src.infrastructure.ffmpeg_processor import FfmpegVideoProcessor
from src.config.transcription_settings import TranscriptionSettings
from src.transcription.interfaces import ITranscriptionService
from src.transcription.providers.whisper_provider import WhisperTranscriptionService

class InfrastructureModule(DIModule):
    def register(self, container: Container) -> None:
        # Register settings
        container.register_singleton(SystemSettings, SystemSettings())
        container.register_singleton(TranscriptionSettings, TranscriptionSettings())
        
        # HTTP Client could be registered as a factory that yields a client
        def create_http_client(c: Container) -> httpx.AsyncClient:
            return httpx.AsyncClient(limits=httpx.Limits(max_keepalive_connections=20, max_connections=100))
            
        container.register_factory(httpx.AsyncClient, create_http_client, singleton=True)

        def create_job_repo(c: Container) -> IJobRepository:
            try:
                session = c.resolve(AsyncSession)
            except KeyError:
                session = AsyncSessionLocal()
            return JobRepository(session)
            
        container.register_factory(IJobRepository, create_job_repo, singleton=False)

        def create_project_repo(c: Container) -> IProjectRepository:
            try:
                session = c.resolve(AsyncSession)
            except KeyError:
                session = AsyncSessionLocal()
            return ProjectRepository(session)
            
        container.register_factory(IProjectRepository, create_project_repo, singleton=False)

        def create_video_repo(c: Container) -> IVideoRepository:
            try:
                session = c.resolve(AsyncSession)
            except KeyError:
                session = AsyncSessionLocal()
            return VideoRepository(session)
            
        container.register_factory(IVideoRepository, create_video_repo, singleton=False)

        # Register Production-Safe Workflow Dispatcher
        container.register_singleton(IWorkflowDispatcher, ApiSafeAsyncWorkflowDispatcher())

        # Register Video Processor
        container.register_singleton(IVideoProcessor, FfmpegVideoProcessor())
        
        # Register Transcription Service
        def create_transcription_service(c: Container) -> ITranscriptionService:
            return WhisperTranscriptionService(c.resolve(TranscriptionSettings))
            
        container.register_factory(ITranscriptionService, create_transcription_service, singleton=True)
