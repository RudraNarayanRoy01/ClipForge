import uuid
from src.domain.campaign_entities import Campaign
from src.domain.ports import ICampaignIntelligence, ICampaignRepository

class GenerateCampaignExecutionPlanUseCase:
    """
    Generates the initial AI execution plan for a campaign based on its rules and summary.
    """
    def __init__(self, intelligence: ICampaignIntelligence, repository: ICampaignRepository):
        self.intelligence = intelligence
        self.repository = repository

    async def execute(self, campaign_id: uuid.UUID) -> Campaign:
        campaign = await self.repository.get_campaign(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
            
        plan = await self.intelligence.generate_execution_plan(campaign)
        campaign.execution_plan = plan
        
        await self.repository.save_campaign(campaign)
        return campaign

class GenerateCampaignClipStrategyUseCase:
    """
    Generates a granular clip strategy based on the established execution plan.
    """
    def __init__(self, intelligence: ICampaignIntelligence, repository: ICampaignRepository):
        self.intelligence = intelligence
        self.repository = repository

    async def execute(self, campaign_id: uuid.UUID) -> Campaign:
        campaign = await self.repository.get_campaign(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        if not campaign.execution_plan:
            raise ValueError("Execution plan must be generated before clip strategy")
            
        strategy = await self.intelligence.generate_clip_strategy(campaign, campaign.execution_plan)
        campaign.clip_strategy = strategy
        
        await self.repository.save_campaign(campaign)
        return campaign

class GenerateCampaignPromptUseCase:
    """
    Generates precise prompt templates for the Video Engine to use during generation.
    """
    def __init__(self, intelligence: ICampaignIntelligence, repository: ICampaignRepository):
        self.intelligence = intelligence
        self.repository = repository

    async def execute(self, campaign_id: uuid.UUID) -> Campaign:
        campaign = await self.repository.get_campaign(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        if not campaign.execution_plan or not campaign.clip_strategy:
            raise ValueError("Execution plan and clip strategy must be generated before prompts")
            
        template = await self.intelligence.generate_prompt_template(campaign, campaign.execution_plan, campaign.clip_strategy)
        campaign.prompt_template = template
        
        await self.repository.save_campaign(campaign)
        return campaign

class AssessCampaignSuitabilityUseCase:
    """
    Evaluates whether the automated clipping engine should attempt this campaign.
    """
    def __init__(self, intelligence: ICampaignIntelligence, repository: ICampaignRepository):
        self.intelligence = intelligence
        self.repository = repository

    async def execute(self, campaign_id: uuid.UUID) -> Campaign:
        campaign = await self.repository.get_campaign(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
            
        assessment = await self.intelligence.assess_suitability(campaign)
        campaign.suitability_assessment = assessment
        
        await self.repository.save_campaign(campaign)
        return campaign
