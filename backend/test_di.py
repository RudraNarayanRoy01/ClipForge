import sys
sys.path.append("d:/My Data/Precious Data/Vibe Code/AI Clipping Platform/backend")

import asyncio
from src.infrastructure.di.container import Container
from src.bootstrap.modules.campaign_module import CampaignModule
from sqlalchemy.ext.asyncio import AsyncSession

async def main():
    global_container = Container()
    CampaignModule().register(global_container)

    child_container = global_container.create_child()
    child_container.register_singleton(AsyncSession, "FakeSession")

    from src.domain.ports import ICampaignRepository
    try:
        repo = child_container.resolve(ICampaignRepository)
        print("Success:", repo)
    except Exception as e:
        print("Failed:", repr(e))

if __name__ == "__main__":
    asyncio.run(main())
