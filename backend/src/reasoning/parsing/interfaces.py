from abc import ABC, abstractmethod
from src.reasoning.normalization.models import NormalizedCampaignText
from .models import StructuredCampaignDocument

class ICampaignStructureParser(ABC):
    """
    Interface for deterministic document structure extraction.
    Transforms normalized campaign text into a structured document representation
    suitable for downstream entity extraction.
    """
    @abstractmethod
    def parse(self, text: NormalizedCampaignText) -> StructuredCampaignDocument:
        """
        Parses a normalized campaign text into a structured document.
        Must preserve ordering, all content, and apply no semantic meaning.
        """
        pass
