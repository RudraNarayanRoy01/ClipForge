from fastapi import APIRouter

from . import project, clips, videos, system, jobs

api_router = APIRouter()

# Include all V1 routers here
api_router.include_router(system.router)
api_router.include_router(project.router)
api_router.include_router(clips.router)
api_router.include_router(videos.router)
api_router.include_router(jobs.router)
