from src.infrastructure.di.container import Container
from src.bootstrap.modules import DIModule
from src.domain.ports import ICampaignRepository
from src.infrastructure.campaign_repository import CampaignRepository
from sqlalchemy.ext.asyncio import AsyncSession

class CampaignModule(DIModule):
    def register(self, container: Container) -> None:
        # We need AsyncSession for CampaignRepository. In a real app, 
        # this might come from a Request scoped dependency or a session factory.
        # For DI registration, we'll register the factory that gets it from the context
        # or bind it at runtime. For now, we bind the class.
        def create_campaign_repo(c: Container) -> ICampaignRepository:
            # Resolving AsyncSession dynamically if available, otherwise 
            # this will raise an error. FastAPI Depends() usually handles sessions.
            # In our Bootstrap pattern, we provide a session factory.
            session = c.resolve(AsyncSession)
            return CampaignRepository(session)
            
        container.register_factory(ICampaignRepository, create_campaign_repo, singleton=False)
