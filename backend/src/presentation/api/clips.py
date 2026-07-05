from fastapi import APIRouter, HTTPException
from typing import List
import uuid

from ..schemas import (
    ClipResponse, ClipListResponse, ClipUpdate, JobAcceptedResponse
)

router = APIRouter(
    prefix="/clips",
    tags=["Clips"]
)

@router.get("/{clip_id}", response_model=ClipResponse, summary="Get Clip Details")
async def get_clip(clip_id: uuid.UUID):
    """Retrieve details for a specific AI generated clip, including virality score."""
    raise HTTPException(status_code=501, detail="Not implemented yet")

@router.patch("/{clip_id}", response_model=ClipResponse, summary="Update Clip Metadata")
async def update_clip(clip_id: uuid.UUID, updates: ClipUpdate):
    """
    Manually override AI clip boundaries or title. 
    Also used for the 'User Approval' workflow step.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")

@router.post("/{clip_id}/export", response_model=JobAcceptedResponse, status_code=202, tags=["Exports"], summary="Export Video Clip")
async def export_clip(clip_id: uuid.UUID):
    """
    Trigger the FFmpeg rendering pipeline to burn subtitles and crop the video.
    Executes in the background.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
