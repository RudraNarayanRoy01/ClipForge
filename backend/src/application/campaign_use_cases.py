import time
import uuid
from typing import List, Optional
from src.domain.campaign_entities import Campaign, CampaignStatus, CampaignImportHistory, DuplicateCampaignError
from src.domain.ports import ICampaignParser, ICampaignIntelligence, ICampaignRepository, ICampaignNormalizationService

class ImportCampaignUseCase:
    """
    Orchestrates the ingestion, parsing, AI extraction, and saving of a Campaign.
    """
    def __init__(
        self,
        parser: ICampaignParser,
        intelligence: ICampaignIntelligence,
        repository: ICampaignRepository,
        normalizer: Optional[ICampaignNormalizationService] = None
    ):
        self.parser = parser
        self.intelligence = intelligence
        self.repository = repository
        self.normalizer = normalizer

    async def execute(self, source: str, content_type: str, force_import: bool = False) -> Campaign:
        start_time = time.time()
        history = CampaignImportHistory(source_type=content_type, processing_status="started")
        await self.repository.save_import_history(history)
        
        # 1. Parse raw input into text
        try:
            raw_text = await self.parser.parse(source, content_type)
        except Exception as e:
            history.processing_status = "failed"
            history.processing_duration_ms = int((time.time() - start_time) * 1000)
            await self.repository.save_import_history(history)
            
            campaign = Campaign(status=CampaignStatus.FAILED, source=source)
            campaign.raw_content = f"Failed to parse source: {str(e)}"
            await self.repository.save_campaign(campaign)
            return campaign
            
        if self.normalizer:
            raw_text = self.normalizer.normalize(raw_text)
            
        # Optional duplicate detection before intelligence
        if not force_import:
            if content_type.lower() == "url":
                duplicates = await self.repository.find_potential_duplicates(campaign_url=source, title="", brand="")
                if duplicates:
                    history.processing_status = "duplicate_detected"
                    history.duplicate_status = "unresolved"
                    history.processing_duration_ms = int((time.time() - start_time) * 1000)
                    await self.repository.save_import_history(history)
                    raise DuplicateCampaignError(str(duplicates[0].id), "URL already exists.")
                    
        # Create initial campaign
        campaign = Campaign(
            source=source,
            raw_content=raw_text,
            status=CampaignStatus.PROCESSING
        )
        if content_type.lower() == "url":
            campaign.campaign_url = source
            
        await self.repository.save_campaign(campaign)
        history.campaign_id = campaign.id
        await self.repository.save_import_history(history)
        
        try:
            # 2. Extract rules
            rules = await self.intelligence.extract_rules(raw_text)
            campaign.rules = rules
            
            # 3. Generate summary
            summary = await self.intelligence.generate_summary(raw_text)
            campaign.summary = summary
            
            if summary.about:
                campaign.title = summary.about[:50] + "..." if len(summary.about) > 50 else summary.about
            
            # Check for duplicates again with title
            if not force_import:
                duplicates = await self.repository.find_potential_duplicates(campaign_url="", title=campaign.title, brand="")
                if duplicates:
                    history.processing_status = "duplicate_detected"
                    history.duplicate_status = "unresolved"
                    history.processing_duration_ms = int((time.time() - start_time) * 1000)
                    await self.repository.save_import_history(history)
                    raise DuplicateCampaignError(str(duplicates[0].id), "Title similarity.")
            
            # 4. Calculate score
            score = await self.intelligence.calculate_worth_it_score(raw_text, rules)
            campaign.worth_it_score = score
                
            campaign.status = CampaignStatus.PROCESSED
            campaign.confidence_score = 0.85
            
            history.processing_status = "success"
            
        except DuplicateCampaignError:
            raise
        except Exception:
            campaign.status = CampaignStatus.FAILED
            history.processing_status = "failed"
        
        # 5. Save final result
        history.processing_duration_ms = int((time.time() - start_time) * 1000)
        await self.repository.save_campaign(campaign)
        await self.repository.save_import_history(history)
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

class GetImportHistoryUseCase:
    """Retrieves campaign import history"""
    def __init__(self, repository: ICampaignRepository):
        self.repository = repository

    async def execute(self, limit: int = 50, skip: int = 0) -> List[CampaignImportHistory]:
        return await self.repository.get_import_history(limit=limit, skip=skip)
