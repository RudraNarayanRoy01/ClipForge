from abc import ABC, abstractmethod
from typing import Any, Dict
from uuid import UUID


class IAssetRepository(ABC):
    """
    Repository contract for accessing media assets.
    Defines boundaries independent of storage implementation.
    """

    @abstractmethod
    async def get_by_id(self, asset_id: UUID) -> Any:
        """Retrieves an asset by its identifier."""
        pass

    @abstractmethod
    async def exists(self, asset_id: UUID) -> bool:
        """Verifies if an asset exists."""
        pass

    @abstractmethod
    async def get_metadata(self, asset_id: UUID) -> Dict[str, Any]:
        """Retrieves metadata for an asset."""
        pass
