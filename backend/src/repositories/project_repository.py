from typing import Sequence, Optional, List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.infrastructure.models import ProjectModel, ClipSegmentModel
from src.domain.ports import IProjectRepository
from src.domain.entities import Project, ClipSegment
from src.domain.entities import TimeRange # Needed if we map ClipSegment

class ProjectRepository(IProjectRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: ProjectModel) -> Project:
        return Project(
            id=uuid.UUID(model.id),
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            status=model.status,
            storage_path=model.storage_path,
            video_count=model.video_count,
            thumbnail_path=model.thumbnail_path
        )

    def _to_model(self, entity: Project) -> ProjectModel:
        return ProjectModel(
            id=str(entity.id),
            name=entity.name,
            description=entity.description,
            created_at=entity.created_at,
            status=entity.status,
            storage_path=entity.storage_path,
            video_count=entity.video_count,
            thumbnail_path=entity.thumbnail_path
        )

    async def create(self, project: Project) -> Project:
        model = self._to_model(project)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def get_by_id(self, project_id: str) -> Optional[Project]:
        result = await self.session.execute(select(ProjectModel).where(ProjectModel.id == project_id))
        model = result.scalars().first()
        return self._to_domain(model) if model else None

    async def get_by_name(self, name: str) -> Optional[Project]:
        result = await self.session.execute(select(ProjectModel).where(ProjectModel.name == name))
        model = result.scalars().first()
        return self._to_domain(model) if model else None

    async def get_all(self, skip: int = 0, limit: int = 50) -> Sequence[Project]:
        result = await self.session.execute(select(ProjectModel).offset(skip).limit(limit))
        return [self._to_domain(m) for m in result.scalars().all()]

    async def delete(self, project: Project) -> None:
        result = await self.session.execute(select(ProjectModel).where(ProjectModel.id == str(project.id)))
        model = result.scalars().first()
        if model:
            await self.session.delete(model)
            await self.session.commit()

    async def count(self) -> int:
        result = await self.session.execute(select(ProjectModel))
        return len(result.scalars().all())

    async def save_project(self, project: Project) -> None:
        # Same as create or update for now to satisfy old interface
        model = self._to_model(project)
        self.session.add(model)
        await self.session.commit()

    async def get_project(self, project_id: uuid.UUID) -> Project:
        proj = await self.get_by_id(str(project_id))
        if not proj:
            raise ValueError(f"Project {project_id} not found")
        return proj

    async def save_clips(self, clips: List[ClipSegment]) -> None:
        for clip in clips:
            model = ClipSegmentModel(
                id=str(clip.id),
                project_id=str(clip.project_id),
                video_asset_id=str(clip.video_asset_id),
                start_time=clip.boundaries.start_time,
                end_time=clip.boundaries.end_time,
                title=clip.title,
                hook_text=clip.hook_text,
                virality_score=clip.virality_score,
                ai_rationale=clip.ai_rationale,
                user_approved=clip.user_approved
            )
            self.session.add(model)
        await self.session.commit()

    async def get_clips_for_video(self, video_asset_id: uuid.UUID) -> List[ClipSegment]:
        result = await self.session.execute(select(ClipSegmentModel).where(ClipSegmentModel.video_asset_id == str(video_asset_id)))
        models = result.scalars().all()
        clips = []
        for m in models:
            c = ClipSegment(
                id=uuid.UUID(m.id),
                project_id=uuid.UUID(m.project_id),
                video_asset_id=uuid.UUID(m.video_asset_id),
                boundaries=TimeRange(m.start_time, m.end_time),
                title=m.title,
                hook_text=m.hook_text,
                virality_score=m.virality_score,
                ai_rationale=m.ai_rationale,
                user_approved=m.user_approved
            )
            clips.append(c)
        return clips
