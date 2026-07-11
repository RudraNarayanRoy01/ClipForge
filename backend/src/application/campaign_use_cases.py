import uuid
from typing import List
from ..domain.campaign_entities import Campaign, CampaignStatus
from ..domain.ports import ICampaignParser, ICampaignIntelligence, ICampaignRepository

class ImportCampaignUseCase:
    """
    Orchestrates the ingestion, parsing, AI extraction, and saving of a Campaign.
    """
    def __init__(
        self,
        parser: ICampaignParser,
        intelligence: ICampaignIntelligence,
        repository: ICampaignRepository
    ):
        self.parser = parser
        self.intelligence = intelligence
        self.repository = repository

    async def execute(self, source: str, content_type: str) -> Campaign:
        # 1. Parse raw input into text
        try:
            raw_text = await self.parser.parse(source, content_type)
        except Exception as e:
            # Create a failed campaign entry if parsing fails early, or just raise.
            # In Clean Architecture, raising a domain exception is good, but for UX, returning a FAILED campaign is often better.
            campaign = Campaign(status=CampaignStatus.FAILED, source=source)
            campaign.raw_content = f"Failed to parse source: {str(e)}"
            await self.repository.save_campaign(campaign)
            return campaign
            
        # Create initial campaign
        campaign = Campaign(
            source=source,
            raw_content=raw_text,
            status=CampaignStatus.PROCESSING
        )
        # Optional: Save intermediate state if process crashes later
        await self.repository.save_campaign(campaign)
        
        try:
            # 2. Extract rules
            rules = await self.intelligence.extract_rules(raw_text)
            campaign.rules = rules
            
            # 3. Generate summary
            summary = await self.intelligence.generate_summary(raw_text)
            campaign.summary = summary
            
            # 4. Calculate score
            score = await self.intelligence.calculate_worth_it_score(raw_text, rules)
            campaign.worth_it_score = score
            
            # Basic metadata extraction (could also be done by LLM)
            # For this sprint, we assume the LLM might have extracted some of this into the summary
            # We'll use the summary details to populate the top-level fields
            if summary.about:
                # Truncate for title if needed
                campaign.title = summary.about[:50] + "..." if len(summary.about) > 50 else summary.about
            
            # if deadline was extracted in a future iteration
            # pass
                
            campaign.status = CampaignStatus.PROCESSED
            campaign.confidence_score = 0.85 # Mock confidence score - could be added to IStructuredOutput
            
        except Exception as e:
            campaign.status = CampaignStatus.FAILED
            # Not appending error to raw_content to prevent losing the actual raw content
            # But we could log it or add an error field
        
        # 5. Save final result
        await self.repository.save_campaign(campaign)
        return campaign


class GetCampaignsUseCase:
    """Retrieves all campaigns"""
    def __init__(self, repository: ICampaignRepository):
        self.repository = repository

    async def execute(self, limit: int = 50, skip: int = 0) -> List[Campaign]:
        return await self.repository.get_all_campaigns(limit=limit, skip=skip)

class GetCampaignUseCase:
    """Retrieves a single campaign"""
    def __init__(self, repository: ICampaignRepository):
        self.repository = repository

    async def execute(self, campaign_id: uuid.UUID) -> Campaign:
        return await self.repository.get_campaign(campaign_id)
