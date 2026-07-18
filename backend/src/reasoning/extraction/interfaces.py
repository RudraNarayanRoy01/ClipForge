from abc import ABC, abstractmethod
from typing import List
from src.reasoning.parsing.models import StructuredCampaignDocument, DocumentSection
from .models import CampaignEntityDocument, CampaignEntity

class ICampaignEntityExtractor(ABC):
    """
    Interface for deterministic business entity extraction.
    Transforms a structured campaign document into typed entities without
    applying semantic evaluation or reasoning.
    """
    @abstractmethod
    def extract(self, document: StructuredCampaignDocument) -> CampaignEntityDocument:
        """
        Extracts strongly typed entities from the structured document.
        """
        pass

class ISpecificEntityExtractor(ABC):
    """
    Interface for focused extractors that identify specific entity types
    from structural elements or sections.
    """
    @abstractmethod
    def can_extract(self, section: DocumentSection) -> bool:
        """
        Determines if this extractor can process the given section.
        """
        pass
        
    @abstractmethod
    def extract_from_section(self, section: DocumentSection) -> List[CampaignEntity]:
        """
        Extracts specific entities from a document section.
        """
        pass
