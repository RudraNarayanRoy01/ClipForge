from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
import uuid
import os
import tempfile

from src.presentation.schemas import (
    CampaignImportRequest, CampaignResponse, CampaignListResponse,
    CampaignRulesSchema, CampaignSummarySchema, WorthItScoreSchema,
    PaginationMeta, CampaignImportHistoryListResponse, CampaignImportHistoryResponse
)
from src.application.campaign_use_cases import ImportCampaignUseCase, GetCampaignsUseCase, GetCampaignUseCase, GetImportHistoryUseCase
from src.application.normalization_service import TextNormalizationService
from src.infrastructure.campaign_repository import CampaignRepository
from src.infrastructure.parsers import CampaignParserFactory
from src.intelligence.services.campaign_intelligence import CampaignIntelligenceService
from src.application.planning_use_cases import (
    GenerateExecutionPlanUseCase, GenerateClipStrategyUseCase,
    GeneratePromptTemplateUseCase, AssessCampaignSuitabilityUseCase,
    PersistPlanningResultsUseCase, RunPlanningPipelineUseCase
)
from src.application.planning_pipeline_service import PlanningPipelineService
from src.intelligence.providers.router import CapabilityRouter
from src.intelligence.providers.capabilities import IStructuredOutput
from src.domain.ports import ICampaignRepository
from src.domain.campaign_entities import Campaign, CampaignNotFoundError, DuplicateCampaignError
from src.infrastructure.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.config.ai_settings import AISettings
from src.intelligence.interfaces.ai_service import IAIService
from src.intelligence.orchestration.default_service import DefaultAIService
from src.intelligence.prompts.manager import PromptManager
from src.intelligence.providers.factory import ProviderFactory

# Singletons for AI Infrastructure
_ai_settings = AISettings()
_prompt_manager = PromptManager(base_dir=os.path.join(os.path.dirname(__file__), '..', '..', 'intelligence', 'prompts'))
_provider_factory = ProviderFactory(_ai_settings)
_ai_service = DefaultAIService(prompt_manager=_prompt_manager, provider_factory=_provider_factory)

def get_ai_service() -> IAIService:
    return _ai_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/campaigns",
    tags=["Campaigns"]
)

# --- Dependency Injection ---
def get_campaign_repository(db: AsyncSession = Depends(get_db)) -> ICampaignRepository:
    return CampaignRepository(db)

def get_campaign_intelligence(ai_service: IAIService = Depends(get_ai_service)) -> CampaignIntelligenceService:
    structured_llm = CapabilityRouter().resolve([IStructuredOutput])
    return CampaignIntelligenceService(structured_llm, ai_service)

def get_import_campaign_use_case(
    repo: ICampaignRepository = Depends(get_campaign_repository),
    intelligence: CampaignIntelligenceService = Depends(get_campaign_intelligence)
) -> ImportCampaignUseCase:
    parser = CampaignParserFactory()
    normalizer = TextNormalizationService()
    return ImportCampaignUseCase(parser, intelligence, repo, normalizer)
def get_campaigns_use_case(repo: ICampaignRepository = Depends(get_campaign_repository)) -> GetCampaignsUseCase:
    return GetCampaignsUseCase(repo)

def get_campaign_use_case(repo: ICampaignRepository = Depends(get_campaign_repository)) -> GetCampaignUseCase:
    return GetCampaignUseCase(repo)

def get_import_history_use_case(repo: ICampaignRepository = Depends(get_campaign_repository)) -> GetImportHistoryUseCase:
    return GetImportHistoryUseCase(repo)

def get_planning_pipeline_service(
    repo: ICampaignRepository = Depends(get_campaign_repository),
    intelligence: CampaignIntelligenceService = Depends(get_campaign_intelligence)
) -> PlanningPipelineService:
    return PlanningPipelineService(
        repository=repo,
        generate_execution_plan_uc=GenerateExecutionPlanUseCase(intelligence),
        generate_clip_strategy_uc=GenerateClipStrategyUseCase(intelligence),
        generate_prompt_template_uc=GeneratePromptTemplateUseCase(intelligence),
        assess_suitability_uc=AssessCampaignSuitabilityUseCase(intelligence),
        persist_results_uc=PersistPlanningResultsUseCase(repo)
    )

def get_run_planning_pipeline_use_case(
    pipeline_service: PlanningPipelineService = Depends(get_planning_pipeline_service)
) -> RunPlanningPipelineUseCase:
    return RunPlanningPipelineUseCase(pipeline_service)

# --- Mappers ---
def map_campaign_to_response(campaign: Campaign) -> CampaignResponse:
    return CampaignResponse(
        id=campaign.id,
        title=campaign.title,
        source=campaign.source,
        brand=campaign.brand,
        campaign_url=campaign.campaign_url,
        platforms=campaign.platforms,
        deadline=campaign.deadline,
        payout=campaign.payout,
        reward_type=campaign.reward_type,
        status=campaign.status.value if hasattr(campaign.status, 'value') else str(campaign.status),
        confidence_score=campaign.confidence_score,
        created_at=campaign.created_at,
        rules=CampaignRulesSchema(**campaign.rules.__dict__) if campaign.rules else None,
        summary=CampaignSummarySchema(**campaign.summary.__dict__) if campaign.summary else None,
        worth_it_score=WorthItScoreSchema(**campaign.worth_it_score.__dict__) if campaign.worth_it_score else None
    )

# --- Routes ---

@router.post("/import", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED, summary="Import Campaign")
async def import_campaign(
    request: CampaignImportRequest,
    use_case: ImportCampaignUseCase = Depends(get_import_campaign_use_case)
):
    """
    Import a campaign from raw text or a URL. 
    The AI Engine will extract rules, generate a summary, and compute a Worth-It score.
    """
    try:
        campaign = await use_case.execute(source=request.source, content_type=request.content_type, force_import=request.force_import)
        return map_campaign_to_response(campaign)
    except DuplicateCampaignError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"message": str(e), "duplicate_id": e.duplicate_id})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except NotImplementedError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error importing campaign: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during import.")

@router.post("/upload", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED, summary="Upload Campaign File")
async def upload_campaign(
    file: UploadFile = File(...),
    content_type: str = Form(..., description="E.g., pdf, email, discord, telegram"),
    force_import: bool = Form(False),
    use_case: ImportCampaignUseCase = Depends(get_import_campaign_use_case)
):
    """Upload a campaign file directly."""
    temp_path = None
    try:
        # Save uploaded file to temp
        fd, temp_path = tempfile.mkstemp()
        with os.fdopen(fd, 'wb') as f:
            content = await file.read()
            f.write(content)
            
        campaign = await use_case.execute(source=temp_path, content_type=content_type, force_import=force_import)
        return map_campaign_to_response(campaign)
    except DuplicateCampaignError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"message": str(e), "duplicate_id": e.duplicate_id})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except NotImplementedError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading campaign: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during upload.")
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

@router.get("/history", response_model=CampaignImportHistoryListResponse, summary="Get Import History")
async def get_import_history(
    skip: int = 0,
    limit: int = 50,
    use_case: GetImportHistoryUseCase = Depends(get_import_history_use_case)
):
    """List all campaign import history records."""
    if limit > 100:
        limit = 100
        
    histories = await use_case.execute(limit=limit, skip=skip)
    
    data = []
    for h in histories:
        data.append(CampaignImportHistoryResponse(
            id=h.id,
            campaign_id=h.campaign_id,
            import_timestamp=h.import_timestamp,
            source_type=h.source_type,
            processing_status=h.processing_status,
            processing_duration_ms=h.processing_duration_ms,
            duplicate_status=h.duplicate_status
        ))
        
    return CampaignImportHistoryListResponse(
        data=data,
        meta=PaginationMeta(
            total_count=len(data),
            skip=skip,
            limit=limit
        )
    )

@router.get("/", response_model=CampaignListResponse, summary="List Campaigns")
async def list_campaigns(
    skip: int = 0,
    limit: int = 50,
    use_case: GetCampaignsUseCase = Depends(get_campaigns_use_case)
):
    """List all imported campaigns with pagination."""
    if limit > 100:
        limit = 100
        
    campaigns = await use_case.execute(limit=limit, skip=skip)
    
    return CampaignListResponse(
        data=[map_campaign_to_response(c) for c in campaigns],
        meta=PaginationMeta(
            total_count=len(campaigns), # Typically we'd query total count, but keeping it simple
            skip=skip,
            limit=limit
        )
    )

@router.get("/{campaign_id}", response_model=CampaignResponse, summary="Get Campaign Details")
async def get_campaign(
    campaign_id: uuid.UUID,
    use_case: GetCampaignUseCase = Depends(get_campaign_use_case)
):
    """Get complete campaign details, rules, and AI analysis by ID."""
    try:
        campaign = await use_case.execute(campaign_id)
        return map_campaign_to_response(campaign)
    except CampaignNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    except Exception as e:
        logger.error(f"Error fetching campaign {campaign_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")
