from abc import ABC, abstractmethod
from typing import List

from src.editing.domain.models.items import Subtitle
from src.editing.domain.models.project import EditingProject


class ISubtitleGenerationService(ABC):
    """
    Service contract for generating subtitle tracks.
    Independent of transcript providers, AI logic, or speech recognition engines.
    """

    @abstractmethod
    async def generate_subtitles(self, project: EditingProject) -> List[Subtitle]:
        """
        Generates subtitles for the given EditingProject.
        """
        pass
