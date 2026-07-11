import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import typing
import dataclasses

from ..domain.campaign_entities import (
    Campaign, CampaignRules, CampaignSummary, WorthItScore, CampaignStatus, CampaignNotFoundError
)
from ..domain.ports import ICampaignRepository
from .models import CampaignModel

class CampaignRepository(ICampaignRepository):
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def save_campaign(self, campaign: Campaign) -> None:
        result = await self.db.execute(select(CampaignModel).filter(CampaignModel.id == str(campaign.id)))
        db_campaign = result.scalars().first()
        
        if not db_campaign:
            db_campaign = CampaignModel(id=str(campaign.id))
            self.db.add(db_campaign)
            
        db_campaign.title = campaign.title
        db_campaign.source = campaign.source
        db_campaign.brand = campaign.brand
        db_campaign.campaign_url = campaign.campaign_url
        db_campaign.platforms = campaign.platforms
        db_campaign.deadline = campaign.deadline
        db_campaign.payout = campaign.payout
        db_campaign.reward_type = campaign.reward_type
        
        # Serialize nested dataclasses to dicts for JSON columns
        db_campaign.rules_json = dataclasses.asdict(campaign.rules) if campaign.rules else None
        db_campaign.summary_json = dataclasses.asdict(campaign.summary) if campaign.summary else None
        db_campaign.worth_it_score_json = dataclasses.asdict(campaign.worth_it_score) if campaign.worth_it_score else None
        
        db_campaign.raw_content = campaign.raw_content
        db_campaign.confidence_score = campaign.confidence_score
        
        # SQLAlchemy Enum uses the python Enum object directly
        db_campaign.status = campaign.status
        
        await self.db.commit()

    async def get_campaign(self, campaign_id: uuid.UUID) -> Campaign:
        result = await self.db.execute(select(CampaignModel).filter(CampaignModel.id == str(campaign_id)))
        db_campaign = result.scalars().first()
        
        if not db_campaign:
            raise CampaignNotFoundError(str(campaign_id))
            
        return self._map_to_domain(db_campaign)

    async def get_all_campaigns(self, limit: int = 50, skip: int = 0) -> List[Campaign]:
        result = await self.db.execute(
            select(CampaignModel)
            .order_by(CampaignModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        db_campaigns = result.scalars().all()
        
        return [self._map_to_domain(db) for db in db_campaigns]
        
    def _map_to_domain(self, db_campaign: typing.Any) -> Campaign:
        rules_json = typing.cast(typing.Dict[str, typing.Any], db_campaign.rules_json)
        rules = CampaignRules(**rules_json) if rules_json else None
        
        summary_json = typing.cast(typing.Dict[str, typing.Any], db_campaign.summary_json)
        summary = CampaignSummary(**summary_json) if summary_json else None
        
        score_json = typing.cast(typing.Dict[str, typing.Any], db_campaign.worth_it_score_json)
        score = WorthItScore(**score_json) if score_json else None
        
        return Campaign(
            id=uuid.UUID(str(db_campaign.id)),
            title=str(db_campaign.title),
            source=str(db_campaign.source),
            brand=str(db_campaign.brand),
            campaign_url=str(db_campaign.campaign_url),
            platforms=db_campaign.platforms or [],
            deadline=db_campaign.deadline,
            payout=str(db_campaign.payout),
            reward_type=str(db_campaign.reward_type),
            rules=rules,
            summary=summary,
            worth_it_score=score,
            raw_content=str(db_campaign.raw_content),
            confidence_score=float(db_campaign.confidence_score),
            created_at=db_campaign.created_at,
            status=db_campaign.status if isinstance(db_campaign.status, CampaignStatus) else CampaignStatus(db_campaign.status)
        )
