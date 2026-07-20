from abc import ABC, abstractmethod

from src.editing.domain.models.export import ExportProfile
from src.editing.domain.models.project import EditingProject


class IExportPlanningService(ABC):
    """
    Service contract for preparing an EditingProject for export.
    Completely independent of rendering logic, FFmpeg, or encoder concepts.
    """

    @abstractmethod
    async def plan_export(self, project: EditingProject) -> ExportProfile:
        """
        Produces export planning information for the given EditingProject.
        """
        pass
