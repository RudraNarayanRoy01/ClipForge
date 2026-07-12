from fastapi import APIRouter, Depends, HTTPException, status
import uuid
from typing import List

from src.infrastructure.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from src.presentation.schemas import PlanningRequest, PlanningResponse, PlanningHistoryResponse, PaginationMeta
from src.infrastructure.campaign_repository import CampaignRepository
from src.application.planning_pipeline_service import PlanningPipelineService
from src.application.planning_use_cases import (
    RunPlanningPipelineUseCase,
    RegeneratePlanningUseCase,
    GetPlanningResultUseCase,
    ListPlanningHistoryUseCase,
    DeletePlanningResultUseCase
)

from src.presentation.api.campaigns import get_planning_pipeline_service, get_campaign_repository

router = APIRouter(tags=["Planning"])

@router.post("/campaigns/{campaign_id}/plan", response_model=PlanningResponse, status_code=status.HTTP_200_OK)
async def generate_planning(
    campaign_id: uuid.UUID,
    request: PlanningRequest = PlanningRequest(),
    pipeline_service: PlanningPipelineService = Depends(get_planning_pipeline_service)
):
    """
    Generates or regenerates a planning pipeline for a campaign.
    If a plan is already generating or completed, returns it unless force_regenerate is True.
    """
    try:
        if request.force_regenerate:
            result = await RegeneratePlanningUseCase(pipeline_service).execute(campaign_id)
        else:
            result = await RunPlanningPipelineUseCase(pipeline_service).execute(campaign_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns/{campaign_id}/plan", response_model=PlanningResponse)
async def get_planning(
    campaign_id: uuid.UUID,
    repository: CampaignRepository = Depends(get_campaign_repository)
):
    """
    Retrieves the latest planning result for a campaign.
    """
    use_case = GetPlanningResultUseCase(repository)
    result = await use_case.execute(campaign_id)
    if result.pipeline_status.value == "not_started":
        raise HTTPException(status_code=404, detail="Planning not found for this campaign.")
    return result

@router.put("/campaigns/{campaign_id}/plan", response_model=PlanningResponse)
async def regenerate_planning(
    campaign_id: uuid.UUID,
    pipeline_service: PlanningPipelineService = Depends(get_planning_pipeline_service)
):
    """
    Explicitly forces regeneration of the planning pipeline, bumping the version.
    """
    use_case = RegeneratePlanningUseCase(pipeline_service)
    try:
        result = await use_case.execute(campaign_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/campaigns/{campaign_id}/plan", status_code=status.HTTP_204_NO_CONTENT)
async def delete_planning(
    campaign_id: uuid.UUID,
    repository: CampaignRepository = Depends(get_campaign_repository)
):
    """
    Deletes (archives) all planning results associated with a campaign.
    """
    use_case = DeletePlanningResultUseCase(repository)
    await use_case.execute(campaign_id)

@router.get("/planning/history", response_model=PlanningHistoryResponse)
async def get_planning_history(
    campaign_id: uuid.UUID,
    repository: CampaignRepository = Depends(get_campaign_repository)
):
    """
    Returns the history of planning results for a specific campaign.
    """
    use_case = ListPlanningHistoryUseCase(repository)
    results = await use_case.execute(campaign_id)
    
    return {
        "data": results,
        "meta": {"total_count": len(results), "skip": 0, "limit": len(results)}
    }
