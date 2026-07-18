from typing import List, Optional
from .interfaces import ICampaignNormalizationPipeline, INormalizer
from .models import NormalizedCampaignText, CampaignSource
from .normalizers import (
    UnicodeNormalizer,
    LineEndingNormalizer,
    ControlCharacterNormalizer,
    WhitespaceNormalizer,
    BulletNormalizer,
    QuoteNormalizer,
    BlankLineNormalizer
)

class DefaultCampaignNormalizationPipeline(ICampaignNormalizationPipeline):
    """
    Default deterministic pipeline for campaign normalization.
    Executes a predefined sequence of INormalizer instances to convert 
    arbitrary text into a canonical representation.
    """
    
    def __init__(self, normalizers: Optional[List[INormalizer]] = None):
        """
        Initializes the pipeline with a sequence of normalizers.
        If None is provided, it uses the default deterministic sequence.
        
        The execution order is explicit and predictable.
        """
        if normalizers is not None:
            self._normalizers = normalizers
        else:
            self._normalizers = [
                UnicodeNormalizer(),
                LineEndingNormalizer(),
                ControlCharacterNormalizer(),
                QuoteNormalizer(),
                WhitespaceNormalizer(),
                BulletNormalizer(),
                BlankLineNormalizer()
            ]

    def normalize(self, raw_text: str, source: CampaignSource = CampaignSource.UNKNOWN) -> NormalizedCampaignText:
        if not raw_text:
            return NormalizedCampaignText(original_text=raw_text, normalized_text="", source=source)
            
        text = raw_text
        for normalizer in self._normalizers:
            text = normalizer.apply(text)
            
        return NormalizedCampaignText(
            original_text=raw_text,
            normalized_text=text,
            source=source
        )
