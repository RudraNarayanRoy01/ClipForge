import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.domain.entities import VideoAsset
from src.domain.ports import IVideoRepository
from src.infrastructure.models import VideoAssetModel

class VideoRepository(IVideoRepository):
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def save_video(self, video: VideoAsset) -> None:
        result = await self.db.execute(select(VideoAssetModel).filter(VideoAssetModel.id == str(video.id)))
        db_video = result.scalars().first()
        
        if not db_video:
            db_video = VideoAssetModel(
                id=str(video.id),
                project_id=str(video.project_id)
            )
            self.db.add(db_video)
            
        db_video.file_path = video.file_path
        db_video.filename = video.filename
        db_video.original_filename = video.original_filename
        db_video.file_extension = video.file_extension
        db_video.mime_type = video.mime_type
        db_video.file_size_bytes = video.file_size_bytes
        db_video.duration = video.duration
        db_video.duration_seconds = video.duration_seconds
        db_video.width = video.width
        db_video.height = video.height
        db_video.fps = video.fps
        db_video.storage_path = video.storage_path
        
        await self.db.commit()

    async def get_video(self, video_id: uuid.UUID) -> VideoAsset:
        result = await self.db.execute(select(VideoAssetModel).filter(VideoAssetModel.id == str(video_id)))
        db_video = result.scalars().first()
        
        if not db_video:
            raise ValueError(f"Video {video_id} not found")
            
        return VideoAsset(
            id=uuid.UUID(db_video.id),
            project_id=uuid.UUID(db_video.project_id),
            file_path=db_video.file_path,
            filename=db_video.filename,
            original_filename=db_video.original_filename,
            file_extension=db_video.file_extension,
            mime_type=db_video.mime_type,
            file_size_bytes=db_video.file_size_bytes,
            duration=db_video.duration,
            duration_seconds=db_video.duration_seconds,
            width=db_video.width,
            height=db_video.height,
            fps=db_video.fps,
            storage_path=db_video.storage_path,
            created_at=db_video.created_at
        )

    async def delete_video(self, video_id: uuid.UUID) -> None:
        result = await self.db.execute(select(VideoAssetModel).filter(VideoAssetModel.id == str(video_id)))
        db_video = result.scalars().first()
        if db_video:
            await self.db.delete(db_video)
            await self.db.commit()

    async def get_videos_for_project(self, project_id: uuid.UUID) -> List[VideoAsset]:
        result = await self.db.execute(select(VideoAssetModel).filter(VideoAssetModel.project_id == str(project_id)))
        db_videos = result.scalars().all()
        
        domain_videos = []
        for db_video in db_videos:
            domain_videos.append(VideoAsset(
                id=uuid.UUID(db_video.id),
                project_id=uuid.UUID(db_video.project_id),
                file_path=db_video.file_path,
                filename=db_video.filename,
                original_filename=db_video.original_filename,
                file_extension=db_video.file_extension,
                mime_type=db_video.mime_type,
                file_size_bytes=db_video.file_size_bytes,
                duration=db_video.duration,
                duration_seconds=db_video.duration_seconds,
                width=db_video.width,
                height=db_video.height,
                fps=db_video.fps,
                storage_path=db_video.storage_path,
                created_at=db_video.created_at
            ))
            
        return domain_videos
