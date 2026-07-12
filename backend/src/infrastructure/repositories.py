import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.domain.entities import Project, ClipSegment, VideoAsset, TimeRange, Resolution, GeneratedCaption
# We technically need an async port interface, but we will adapt the existing one conceptually
from src.infrastructure.models import ProjectModel, ClipSegmentModel

class AsyncSqliteProjectRepository:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def save_project(self, project: Project) -> None:
        result = await self.db.execute(select(ProjectModel).filter(ProjectModel.id == str(project.id)))
        db_project = result.scalars().first()
        
        if not db_project:
            db_project = ProjectModel(
                id=str(project.id),
                name=project.name,
                created_at=project.created_at,
                status=project.status,
                storage_path=project.storage_path
            )
            self.db.add(db_project)
        else:
            db_project.name = project.name
            db_project.status = project.status
            db_project.storage_path = project.storage_path
            
        await self.db.commit()

    async def get_project(self, project_id: uuid.UUID) -> Project:
        result = await self.db.execute(select(ProjectModel).filter(ProjectModel.id == str(project_id)))
        db_project = result.scalars().first()
        
        if not db_project:
            raise ValueError(f"Project {project_id} not found")
            
        return Project(
            id=uuid.UUID(db_project.id),
            name=db_project.name,
            created_at=db_project.created_at,
            status=db_project.status,
            storage_path=db_project.storage_path
        )

    async def save_clips(self, clips: List[ClipSegment]) -> None:
        for clip in clips:
            result = await self.db.execute(select(ClipSegmentModel).filter(ClipSegmentModel.id == str(clip.id)))
            db_clip = result.scalars().first()
            
            if not db_clip:
                db_clip = ClipSegmentModel(
                    id=str(clip.id),
                    project_id=str(clip.project_id),
                    video_asset_id=str(clip.video_asset_id)
                )
                self.db.add(db_clip)
                
            db_clip.start_time = clip.boundaries.start_time
            db_clip.end_time = clip.boundaries.end_time
            db_clip.title = clip.title
            db_clip.hook_text = clip.hook_text
            db_clip.hashtags = clip.hashtags
            db_clip.thumbnail_timestamp = clip.thumbnail_timestamp
            db_clip.virality_score = clip.virality_score
            db_clip.ai_rationale = clip.ai_rationale
            db_clip.user_approved = clip.user_approved
            
            db_clip.captions = [
                {"start_time": c.time_range.start_time, "end_time": c.time_range.end_time, "text": c.text, "style_metadata": c.style_metadata}
                for c in clip.captions
            ]
            
        await self.db.commit()

    async def get_clips_for_video(self, video_asset_id: uuid.UUID) -> List[ClipSegment]:
        result = await self.db.execute(select(ClipSegmentModel).filter(ClipSegmentModel.video_asset_id == str(video_asset_id)))
        db_clips = result.scalars().all()
        
        domain_clips = []
        for c in db_clips:
            clip = ClipSegment(
                id=uuid.UUID(c.id),
                project_id=uuid.UUID(c.project_id),
                video_asset_id=uuid.UUID(c.video_asset_id),
                boundaries=TimeRange(c.start_time, c.end_time),
                title=c.title,
                hook_text=c.hook_text,
                hashtags=c.hashtags,
                thumbnail_timestamp=c.thumbnail_timestamp,
                virality_score=c.virality_score,
                ai_rationale=c.ai_rationale,
                user_approved=c.user_approved
            )
            clip.captions = [
                GeneratedCaption(time_range=TimeRange(cap["start_time"], cap["end_time"]), text=cap["text"], style_metadata=cap["style_metadata"])
                for cap in c.captions
            ]
            domain_clips.append(clip)
            
        return domain_clips
