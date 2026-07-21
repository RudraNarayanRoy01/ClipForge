import uuid
import time
import logging

from src.domain.campaign_entities import PlanningPipelineResult, PipelineStatus, ValidationStatus
from src.domain.ports import ICampaignRepository
from src.domain.errors import PlanningError, InfrastructureError, DomainError, ValidationError
from src.application.planning_use_cases import (
    GenerateExecutionPlanUseCase,
    GenerateClipStrategyUseCase,
    GeneratePromptTemplateUseCase,
    AssessCampaignSuitabilityUseCase,
    PersistPlanningResultsUseCase
)
from src.reasoning.normalization.pipeline import DefaultCampaignNormalizationPipeline
from src.reasoning.normalization.models import CampaignSource

logger = logging.getLogger(__name__)

class PlanningPipelineService:
    """
    Orchestrates the campaign planning process through a deterministic state machine.
    Handles error recovery, auditing, and structured logging.
    """
    def __init__(
        self, 
        repository: ICampaignRepository,
        generate_execution_plan_uc: GenerateExecutionPlanUseCase,
        generate_clip_strategy_uc: GenerateClipStrategyUseCase,
        generate_prompt_template_uc: GeneratePromptTemplateUseCase,
        assess_suitability_uc: AssessCampaignSuitabilityUseCase,
        persist_results_uc: PersistPlanningResultsUseCase
    ):
        self.repository = repository
        self.generate_execution_plan_uc = generate_execution_plan_uc
        self.generate_clip_strategy_uc = generate_clip_strategy_uc
        self.generate_prompt_template_uc = generate_prompt_template_uc
        self.assess_suitability_uc = assess_suitability_uc
        self.persist_results_uc = persist_results_uc

    async def run_pipeline(self, campaign_id: uuid.UUID, force_regenerate: bool = False) -> PlanningPipelineResult:
        pipeline_start_time = time.time()
        
        try:
            campaign = await self.repository.get_campaign(campaign_id)
            if not campaign:
                raise PlanningError(f"Campaign {campaign_id} not found for planning pipeline.")
        except Exception as e:
            logger.error("pipeline_failed", extra={"campaign_id": str(campaign_id), "stage": "init", "reason": "Repository failure"}, exc_info=True)
            raise InfrastructureError(f"Failed to load campaign: {e}") from e

        # Load or initialize the result
        result = await self.repository.get_planning_result(campaign_id)
        
        if force_regenerate and result.pipeline_status != PipelineStatus.NOT_STARTED:
            result = PlanningPipelineResult(
                campaign_id=campaign_id,
                planner_model="unknown",
                planning_version="unknown",
                version=result.version + 1
            )
            logger.info("Forcing Pipeline Regeneration", extra={"campaign_id": str(campaign_id), "new_version": result.version})
        else:
            if result.pipeline_status in (PipelineStatus.COMPLETED, PipelineStatus.RUNNING):
                logger.info("Pipeline Skipped", extra={"campaign_id": str(campaign_id), "status": result.pipeline_status.value})
                return result

        logger.info(
            "Pipeline Started",
            extra={
                "campaign_id": str(campaign_id),
                "pipeline_version": result.planning_version or "1.0.0",
                "initial_status": result.pipeline_status.value
            }
        )

        if result.pipeline_status in (PipelineStatus.NOT_STARTED, PipelineStatus.FAILED):
            result.pipeline_status = PipelineStatus.RUNNING
            await self.persist_results_uc.execute(result)

        try:
            # Stage 0: Normalization and Initial Validation
            logger.info("Stage Started", extra={"campaign_id": str(campaign_id), "stage": "normalization_and_validation"})
            normalizer = DefaultCampaignNormalizationPipeline()
            normalized_result = normalizer.normalize(campaign.raw_content, source=CampaignSource.UNKNOWN)
            
            if not normalized_result.normalized_text.strip():
                raise ValidationError("Campaign content is empty after normalization. Cannot proceed with planning.")
            
            # The campaign content is now validated as non-empty and canonical.
            # In a full implementation we would persist the normalized_text on the campaign object.
            
            logger.info("Stage Finished", extra={"campaign_id": str(campaign_id), "stage": "normalization_and_validation"})

            # Stage 1: Execution Plan
            if not result.execution_plan:
                stage_start = time.time()
                logger.info("Stage Started", extra={"campaign_id": str(campaign_id), "stage": "execution_plan"})
                result.execution_plan = await self.generate_execution_plan_uc.execute(campaign)
                result.planner_model = getattr(result.execution_plan, "planner_model", result.planner_model)
                result.planning_version = getattr(result.execution_plan, "planning_version", result.planning_version)
                result.pipeline_status = PipelineStatus.EXECUTION_PLAN_COMPLETE
                await self.persist_results_uc.execute(result)
                logger.info("Stage Finished", extra={
                    "campaign_id": str(campaign_id), 
                    "stage": "execution_plan", 
                    "execution_duration": time.time() - stage_start,
                    "confidence": getattr(result.execution_plan, "confidence_score", 0.0)
                })

            # Stage 2: Clip Strategy
            if not result.clip_strategy and result.execution_plan:
                stage_start = time.time()
                logger.info("Stage Started", extra={"campaign_id": str(campaign_id), "stage": "clip_strategy"})
                result.clip_strategy = await self.generate_clip_strategy_uc.execute(campaign, result.execution_plan)
                result.pipeline_status = PipelineStatus.CLIP_STRATEGY_COMPLETE
                await self.persist_results_uc.execute(result)
                logger.info("Stage Finished", extra={"campaign_id": str(campaign_id), "stage": "clip_strategy", "execution_duration": time.time() - stage_start})

            # Stage 3: Prompt Template
            if not result.prompt_template and result.execution_plan and result.clip_strategy:
                stage_start = time.time()
                logger.info("Stage Started", extra={"campaign_id": str(campaign_id), "stage": "prompt_template"})
                result.prompt_template = await self.generate_prompt_template_uc.execute(campaign, result.execution_plan, result.clip_strategy)
                result.pipeline_status = PipelineStatus.PROMPT_TEMPLATE_COMPLETE
                await self.persist_results_uc.execute(result)
                logger.info("Stage Finished", extra={"campaign_id": str(campaign_id), "stage": "prompt_template", "execution_duration": time.time() - stage_start})

            # Stage 4: Suitability Assessment
            if not result.suitability_assessment:
                stage_start = time.time()
                logger.info("Stage Started", extra={"campaign_id": str(campaign_id), "stage": "suitability_assessment"})
                result.suitability_assessment = await self.assess_suitability_uc.execute(campaign)
                result.pipeline_status = PipelineStatus.SUITABILITY_COMPLETE
                
                # Derive overall confidence deterministically
                result.compute_overall_confidence()
                
                await self.persist_results_uc.execute(result)
                logger.info("Stage Finished", extra={
                    "campaign_id": str(campaign_id), 
                    "stage": "suitability_assessment", 
                    "execution_duration": time.time() - stage_start,
                    "confidence": getattr(result.suitability_assessment, "confidence", 0.0)
                })

            # Mark Completed
            result.pipeline_status = PipelineStatus.COMPLETED
            result.execution_duration_ms += int((time.time() - pipeline_start_time) * 1000)
            
            result.compute_overall_confidence()
            result.validate_consistency()
            
            if result.overall_confidence >= 0.7:
                result.validation_status = ValidationStatus.VALID
            else:
                result.validation_status = ValidationStatus.INVALID
                
            await self.persist_results_uc.execute(result)
            
            logger.info(
                "Pipeline Completed",
                extra={
                    "campaign_id": str(campaign_id),
                    "execution_duration": result.execution_duration_ms,
                    "overall_confidence": result.overall_confidence,
                    "validation_status": result.validation_status.value,
                    "pipeline_version": result.planning_version,
                    "planner_model": result.planner_model
                }
            )
            return result

        except DomainError as e:
            logger.error(
                "Stage Failed",
                extra={
                    "campaign_id": str(campaign_id),
                    "failure_reason": str(e),
                    "stage": result.pipeline_status.value,
                    "error_category": e.__class__.__name__
                }
            )
            result.pipeline_status = PipelineStatus.FAILED
            result.execution_duration_ms += int((time.time() - pipeline_start_time) * 1000)
            await self.persist_results_uc.execute(result)
            raise
        except Exception as e:
            logger.error(
                "Stage Failed",
                extra={
                    "campaign_id": str(campaign_id),
                    "failure_reason": "Unhandled internal error",
                    "stage": result.pipeline_status.value,
                    "error_category": "InfrastructureError"
                },
                exc_info=True
            )
            result.pipeline_status = PipelineStatus.FAILED
            result.execution_duration_ms += int((time.time() - pipeline_start_time) * 1000)
            await self.persist_results_uc.execute(result)
            raise InfrastructureError(f"Unexpected pipeline error: {str(e)}") from e
