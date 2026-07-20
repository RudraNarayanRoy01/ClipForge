from abc import ABC, abstractmethod
from typing import Any, Dict, List

from src.editing.domain.models.items import Clip
from src.editing.domain.models.project import EditingProject


class IEditingService(ABC):
    """
    Service contract for generating the editing sequence.
    """

    @abstractmethod
    async def generate_edit_sequence(
        self, 
        project: EditingProject, 
        clips: List[Clip]
    ) -> Dict[str, Any]:
        """
        Generates metadata for the editing sequence based on clips.
        """
        pass
