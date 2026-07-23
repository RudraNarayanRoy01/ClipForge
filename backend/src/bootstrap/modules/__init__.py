from typing import Protocol
from src.infrastructure.di.container import Container

class DIModule(Protocol):
    """
    Protocol for Dependency Injection modules.
    Each module is responsible for registering its domain's dependencies into the Container.
    """
    def register(self, container: Container) -> None:
        ...
