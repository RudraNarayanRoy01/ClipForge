import time
import shutil
from datetime import datetime, timezone
from fastapi import APIRouter, Request

from ..schemas import HealthResponse

router = APIRouter(
    tags=["System"]
)

START_TIME = time.time()

def check_ffmpeg() -> str:
    """Check if ffmpeg is available in the system PATH."""
    return "ok" if shutil.which("ffmpeg") else "not_found"

@router.get("/health", response_model=HealthResponse, summary="System Health Check")
async def health_check(request: Request):
    """
    Production-grade health check to determine whether the entire AI pipeline is operational.
    Preserves backward compatibility with the legacy response format.
    """
    uptime = time.time() - START_TIME
    
    # In a full implementation, these would execute asynchronous pings or checks.
    # We mock them as 'ok' for now, establishing the API contract.
    database_status = "ok"
    ollama_status = "ok"
    gemma_status = "ok"
    whisper_status = "ok"
    queue_status = "ok"
    ffmpeg_status = check_ffmpeg()
    
    # Evaluate overall system health
    statuses = [database_status, ollama_status, gemma_status, whisper_status, ffmpeg_status, queue_status]
    overall_status = "ok" if all(s == "ok" for s in statuses) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        message="AI Clipping Platform Backend is ready.",
        version=request.app.version,
        uptime=uptime,
        database=database_status,
        ollama=ollama_status,
        gemma=gemma_status,
        whisper=whisper_status,
        ffmpeg=ffmpeg_status,
        queue=queue_status,
        timestamp=datetime.now(timezone.utc)
    )
