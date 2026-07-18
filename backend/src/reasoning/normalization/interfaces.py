from abc import ABC, abstractmethod
from typing import Protocol
from .models import NormalizedCampaignText, CampaignSource

class INormalizer(ABC):
    """
    Interface for a single, deterministic text normalization step.
    Must be idempotent.
    """
    @abstractmethod
    def apply(self, text: str) -> str:
        """
        Applies a deterministic transformation to the input text.
        """
        pass

class ICampaignNormalizationPipeline(ABC):
    """
    Interface for the campaign normalization pipeline.
    Responsible for orchestrating the execution of INormalizer instances
    to convert raw text into a canonical NormalizedCampaignText.
    """
    @abstractmethod
    def normalize(self, raw_text: str, source: CampaignSource = CampaignSource.UNKNOWN) -> NormalizedCampaignText:
        """
        Executes the normalization pipeline on the raw text.
        """
        pass
