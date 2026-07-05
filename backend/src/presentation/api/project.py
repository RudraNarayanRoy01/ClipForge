from fastapi import APIRouter, Depends, HTTPException, status
import uuid

from ..schemas import ProjectCreate, ProjectResponse, ProjectListResponse
from ...services.project_service import ProjectService
from ...repositories.project_repository import ProjectRepository
from ...infrastructure.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    repo = ProjectRepository(db)
    return ProjectService(repo)

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
