from typing import List

from src.reasoning.parsing.models import StructuredCampaignDocument
from .models import (
    CampaignEntityDocument,
    CampaignRequirement,
    CampaignRestriction,
    CampaignPlatform,
    CampaignRegion,
    CampaignReward,
    CampaignDeadline,
    CampaignDeliverable,
    CampaignAudioRule,
    CampaignHashtag,
    CampaignNote
)
from .interfaces import ICampaignEntityExtractor
from .extractors import (
    RequirementExtractor,
    RestrictionExtractor,
    PlatformExtractor,
    RegionExtractor,
    RewardExtractor,
    DeadlineExtractor,
    DeliverableExtractor,
    AudioRuleExtractor,
    HashtagExtractor,
    NoteExtractor
)

class DefaultCampaignEntityExtractor(ICampaignEntityExtractor):
    """
    Default orchestrator for campaign entity extraction.
    Delegates extraction to focused specific extractors based on structural context.
    """
    def __init__(self):
        # Register focused extractors. Order matters for matching.
        self._extractors = [
            RequirementExtractor(),
            RestrictionExtractor(),
            PlatformExtractor(),
            RegionExtractor(),
            RewardExtractor(),
            DeadlineExtractor(),
            DeliverableExtractor(),
            AudioRuleExtractor(),
            HashtagExtractor()
        ]
        self._fallback_extractor = NoteExtractor()

    def extract(self, document: StructuredCampaignDocument) -> CampaignEntityDocument:
        doc = CampaignEntityDocument()
        
        for section in document.sections:
            matched_extractor = None
            
            # Find the first specific extractor that can handle this section
            for extractor in self._extractors:
                if extractor.can_extract(section):
                    matched_extractor = extractor
                    break
            
            # If no specific match, fallback to NoteExtractor
            if not matched_extractor:
                matched_extractor = self._fallback_extractor
                
            entities = matched_extractor.extract_from_section(section)
            
            # Distribute the extracted entities into the document collections
            for entity in entities:
                if isinstance(entity, CampaignRequirement):
                    doc.requirements.append(entity)
                elif isinstance(entity, CampaignRestriction):
                    doc.restrictions.append(entity)
                elif isinstance(entity, CampaignPlatform):
                    doc.platforms.append(entity)
                elif isinstance(entity, CampaignRegion):
                    doc.regions.append(entity)
                elif isinstance(entity, CampaignReward):
                    doc.rewards.append(entity)
                elif isinstance(entity, CampaignDeadline):
                    doc.deadlines.append(entity)
                elif isinstance(entity, CampaignDeliverable):
                    doc.deliverables.append(entity)
                elif isinstance(entity, CampaignAudioRule):
                    doc.audio_rules.append(entity)
                elif isinstance(entity, CampaignHashtag):
                    doc.hashtags.append(entity)
                elif isinstance(entity, CampaignNote):
                    doc.notes.append(entity)
                    
        return doc
