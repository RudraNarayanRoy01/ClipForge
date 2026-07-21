import uuid
from typing import Optional

from src.domain.entities import Project
from src.domain.ports import IProjectRepository

class ProjectService:
    def __init__(self, repository: IProjectRepository):
        self.repository = repository

    async def create_project(self, name: str, description: Optional[str] = None) -> Project:
        name = name.strip()
        if not name:
            raise ValueError("Project name cannot be empty")

        existing_project = await self.repository.get_by_name(name)
        if existing_project:
            raise ValueError("A project with this name already exists")

        project_id = uuid.uuid4()
        # Generate storage path but do not create folder as per sprint rules
        storage_path = f"/data/projects/{project_id}"

        new_project = Project(
            id=project_id,
            name=name,
            description=description,
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

    async def get_project(self, project_id: str) -> Project:
        project = await self.repository.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found")
        return project

    async def delete_project(self, project_id: str) -> None:
        project = await self.repository.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found")
        await self.repository.delete(project)
