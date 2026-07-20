from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID


class IRenderArtifactRepository(ABC):
    """
    Repository contract for completed render outputs.
    Manages references and metadata, independent of rendering engines.
    """

    @abstractmethod
    async def save_metadata(self, project_id: UUID, metadata: Dict[str, Any]) -> None:
        """Saves metadata for a render artifact."""
        pass

    @abstractmethod
    async def get_by_id(self, artifact_id: UUID) -> Optional[Any]:
        """Retrieves a render artifact reference by ID."""
        pass

    @abstractmethod
    async def get_latest_for_project(self, project_id: UUID) -> Optional[Any]:
        """Retrieves the latest render artifact for a given project."""
        pass

    @abstractmethod
    async def list_for_project(self, project_id: UUID) -> List[Any]:
        """Lists historical render outputs for a given project."""
        pass
