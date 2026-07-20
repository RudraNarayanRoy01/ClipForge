from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.editing.domain.models.project import EditingProject


class IEditingProjectRepository(ABC):
    """
    Repository contract for EditingProject aggregate.
    Defines persistence boundaries without infrastructure details.
    """

    @abstractmethod
    async def save(self, project: EditingProject) -> None:
        """Saves an EditingProject."""
        pass

    @abstractmethod
    async def get_by_id(self, project_id: UUID) -> Optional[EditingProject]:
        """Loads an EditingProject by its ID."""
        pass

    @abstractmethod
    async def delete(self, project_id: UUID) -> None:
        """Deletes an EditingProject."""
        pass

    @abstractmethod
    async def get_all(self, limit: int = 50, skip: int = 0) -> List[EditingProject]:
        """Retrieves a list of EditingProjects."""
        pass

    @abstractmethod
    async def exists(self, project_id: UUID) -> bool:
        """Checks if an EditingProject exists."""
        pass
