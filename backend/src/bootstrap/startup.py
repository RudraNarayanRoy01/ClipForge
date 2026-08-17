from src.infrastructure.di.container import Container
from src.bootstrap.modules.infrastructure_module import InfrastructureModule
from src.bootstrap.modules.intelligence_module import IntelligenceModule
from src.bootstrap.modules.campaign_module import CampaignModule
from src.bootstrap.modules.runtime_module import RuntimeModule

_global_container = Container()

def initialize_container() -> Container:
    """Initialize the global DI container with all modules."""
    # Register modules
    modules = [
        InfrastructureModule(),
        IntelligenceModule(),
        CampaignModule(),
        RuntimeModule()
    ]

    for module in modules:
        module.register(_global_container)

    return _global_container

def get_container() -> Container:
    """Access the global DI container."""
    return _global_container
