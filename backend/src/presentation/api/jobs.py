from fastapi import APIRouter, HTTPException
import uuid
from typing import Dict, Any

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)

@router.get("/{job_id}", summary="Get Job Status")
async def get_job_status(job_id: uuid.UUID) -> Dict[str, Any]:
    """
    Poll the status of an asynchronous background job (e.g., video analysis or clip export).
    """
    # TODO: In Milestone 2, connect to the actual Job Repository or Celery backend.
    raise HTTPException(status_code=501, detail="Not implemented yet")
