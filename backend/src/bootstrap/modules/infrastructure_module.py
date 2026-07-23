import httpx
from src.infrastructure.di.container import Container
from src.bootstrap.modules import DIModule
from src.config.system_settings import SystemSettings
from src.infrastructure.database import get_db

class InfrastructureModule(DIModule):
    def register(self, container: Container) -> None:
        # Register settings
        container.register_singleton(SystemSettings, SystemSettings())
        
        # HTTP Client could be registered as a factory that yields a client
        def create_http_client(c: Container) -> httpx.AsyncClient:
            return httpx.AsyncClient(limits=httpx.Limits(max_keepalive_connections=20, max_connections=100))
            
        container.register_factory(httpx.AsyncClient, create_http_client, singleton=True)
