import uuid
from typing import Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.infrastructure.models import ProjectModel

class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, project: ProjectModel) -> ProjectModel:
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def get_by_id(self, project_id: str) -> Optional[ProjectModel]:
        result = await self.session.execute(select(ProjectModel).where(ProjectModel.id == project_id))
        return result.scalars().first()

    async def get_by_name(self, name: str) -> Optional[ProjectModel]:
        result = await self.session.execute(select(ProjectModel).where(ProjectModel.name == name))
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 50) -> Sequence[ProjectModel]:
        result = await self.session.execute(select(ProjectModel).offset(skip).limit(limit))
        return result.scalars().all()

    async def delete(self, project: ProjectModel) -> None:
        await self.session.delete(project)
        await self.session.commit()

    async def count(self) -> int:
        # A simple count, in a real app use func.count()
        result = await self.session.execute(select(ProjectModel))
        return len(result.scalars().all())
