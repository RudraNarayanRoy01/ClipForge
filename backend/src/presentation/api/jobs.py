from fastapi import APIRouter, HTTPException, Depends
import uuid
from typing import Dict, Any

from src.domain.ports import IJobRepository
from src.workers.state.job_repository import global_job_repository

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)

def get_job_repository() -> IJobRepository:
    return global_job_repository

@router.get("/{job_id}", summary="Get Job Status")
async def get_job_status(job_id: uuid.UUID, repo: IJobRepository = Depends(get_job_repository)) -> Dict[str, Any]:
    """
    Poll the status of an asynchronous background job (e.g., video analysis or clip export).
    """
    job = await repo.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response: Dict[str, Any] = {
        "job_id": str(job.id),
        "status": job.status,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }
    
    if job.error:
        response["error"] = job.error
    if job.result:
        response["result"] = job.result
        
    return response
