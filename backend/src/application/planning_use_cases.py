import uuid
from src.domain.campaign_entities import (
    Campaign, CampaignExecutionPlan, CampaignClipStrategy, 
    CampaignPromptTemplate, CampaignSuitabilityAssessment, PlanningPipelineResult
)
from typing import TYPE_CHECKING
from src.domain.ports import ICampaignIntelligence, ICampaignRepository

if TYPE_CHECKING:
    from src.application.planning_pipeline_service import PlanningPipelineService

class GenerateExecutionPlanUseCase:
    """
    Generates the initial AI execution plan for a campaign based on its rules and summary.
    Does not persist the result.
    """
    def __init__(self, intelligence: ICampaignIntelligence):
        self.intelligence = intelligence

    async def execute(self, campaign: Campaign) -> CampaignExecutionPlan:
        plan = await self.intelligence.generate_execution_plan(campaign)
        return plan

class GenerateClipStrategyUseCase:
    """
    Generates a granular clip strategy based on the established execution plan.
    Does not persist the result.
    """
    def __init__(self, intelligence: ICampaignIntelligence):
        self.intelligence = intelligence

    async def execute(self, campaign: Campaign, execution_plan: CampaignExecutionPlan) -> CampaignClipStrategy:
        strategy = await self.intelligence.generate_clip_strategy(campaign, execution_plan)
        return strategy

class GeneratePromptTemplateUseCase:
    """
    Generates precise prompt templates for the Video Engine to use during generation.
    Does not persist the result.
    """
    def __init__(self, intelligence: ICampaignIntelligence):
        self.intelligence = intelligence

    async def execute(self, campaign: Campaign, execution_plan: CampaignExecutionPlan, clip_strategy: CampaignClipStrategy) -> CampaignPromptTemplate:
        template = await self.intelligence.generate_prompt_template(campaign, execution_plan, clip_strategy)
        return template

class AssessCampaignSuitabilityUseCase:
    """
    Evaluates whether the automated clipping engine should attempt this campaign.
    Does not persist the result.
    """
    def __init__(self, intelligence: ICampaignIntelligence):
        self.intelligence = intelligence

    async def execute(self, campaign: Campaign) -> CampaignSuitabilityAssessment:
        assessment = await self.intelligence.assess_suitability(campaign)
        return assessment

class PersistPlanningResultsUseCase:
    """
    Persists a complete or partially complete PlanningPipelineResult.
    """
    def __init__(self, repository: ICampaignRepository):
        self.repository = repository

    async def execute(self, result: PlanningPipelineResult) -> None:
        await self.repository.save_planning_result(result)

class RunPlanningPipelineUseCase:
    """
    Triggers the execution of the full planning pipeline for a campaign.
    """
    def __init__(self, pipeline_service: 'PlanningPipelineService'):
        self.pipeline_service = pipeline_service

    async def execute(self, campaign_id: uuid.UUID) -> PlanningPipelineResult:
        return await self.pipeline_service.run_pipeline(campaign_id)
