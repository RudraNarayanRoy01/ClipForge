import uuid
from typing import Sequence, Optional
from datetime import datetime, timezone
from fastapi import HTTPException

from src.infrastructure.models import ProjectModel
from src.repositories.project_repository import ProjectRepository
from src.presentation.schemas import ProjectCreate

class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    async def create_project(self, project_data: ProjectCreate) -> ProjectModel:
        name = project_data.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Project name cannot be empty")

        existing_project = await self.repository.get_by_name(name)
        if existing_project:
            raise HTTPException(status_code=409, detail="A project with this name already exists")

        project_id = str(uuid.uuid4())
        # Generate storage path but do not create folder as per sprint rules
        storage_path = f"/data/projects/{project_id}"

        new_project = ProjectModel(
            id=project_id,
            name=name,
            description=getattr(project_data, 'description', None),
            storage_path=storage_path,
            status="EMPTY",
            video_count=0
        )

        return await self.repository.create(new_project)

    async def list_projects(self, skip: int = 0, limit: int = 50) -> dict:
        projects = await self.repository.get_all(skip=skip, limit=limit)
        total_count = await self.repository.count()
        return {
            "data": projects,
            "meta": {
                "total_count": total_count,
                "skip": skip,
                "limit": limit
            }
        }

    async def get_project(self, project_id: str) -> ProjectModel:
        project = await self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    async def delete_project(self, project_id: str) -> None:
        project = await self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        await self.repository.delete(project)
