import re
from typing import List, Type, Any

from src.reasoning.parsing.models import (
    DocumentSection,
    DocumentElement,
    ParagraphBlock,
    BulletListBlock,
    NumberedListBlock,
    SeparatorBlock
)
from .models import (
    CampaignEntity,
    EntitySourceReference,
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
from .interfaces import ISpecificEntityExtractor

def _get_element_text(element: DocumentElement) -> str:
    if isinstance(element, (ParagraphBlock, BulletListBlock, NumberedListBlock)):
        return "\n".join(element.original_lines)
    elif isinstance(element, SeparatorBlock):
        return element.original_line
    return ""

def _get_element_lines(element: DocumentElement) -> tuple[int, int]:
    if hasattr(element, "start_line") and hasattr(element, "end_line"):
        return getattr(element, "start_line"), getattr(element, "end_line")
    return 0, 0

class BaseSectionExtractor(ISpecificEntityExtractor):
    """
    Base extractor that maps a matched section's elements to a specific entity class.
    """
    def __init__(self, entity_class: Type[CampaignEntity], keywords: List[str]):
        self.entity_class = entity_class
        self.keywords = [k.lower() for k in keywords]
        
    def can_extract(self, section: DocumentSection) -> bool:
        if not section.title:
            return False
        title_lower = section.title.lower()
        return any(keyword in title_lower for keyword in self.keywords)
        
    def extract_from_section(self, section: DocumentSection) -> List[CampaignEntity]:
        entities = []
        for i, element in enumerate(section.elements):
            if isinstance(element, SeparatorBlock):
                continue
                
            text = _get_element_text(element)
            start_line, end_line = _get_element_lines(element)
            
            source_ref = EntitySourceReference(
                section_position=section.position,
                element_index=i,
                start_line=start_line,
                end_line=end_line
            )
            
            entities.append(self.entity_class(
                original_text=text,
                source_reference=source_ref
            ))
        return entities

class RequirementExtractor(BaseSectionExtractor):
    def __init__(self):
        super().__init__(CampaignRequirement, ["requirement", "criteria", "must", "qualification"])

class RestrictionExtractor(BaseSectionExtractor):
    def __init__(self):
        super().__init__(CampaignRestriction, ["restriction", "do not", "prohibited", "banned"])

class PlatformExtractor(BaseSectionExtractor):
    def __init__(self):
        super().__init__(CampaignPlatform, ["platform", "social media", "channel", "network"])

class RegionExtractor(BaseSectionExtractor):
    def __init__(self):
        super().__init__(CampaignRegion, ["region", "country", "location", "geography"])

class RewardExtractor(BaseSectionExtractor):
    def __init__(self):
        super().__init__(CampaignReward, ["reward", "payout", "compensation", "payment", "bounty"])

class DeadlineExtractor(BaseSectionExtractor):
    def __init__(self):
        super().__init__(CampaignDeadline, ["deadline", "timeline", "due date", "schedule"])

class DeliverableExtractor(BaseSectionExtractor):
    def __init__(self):
        super().__init__(CampaignDeliverable, ["deliverable", "content type", "format", "video type"])

class AudioRuleExtractor(BaseSectionExtractor):
    def __init__(self):
        super().__init__(CampaignAudioRule, ["audio", "music", "sound", "soundtrack"])

class HashtagExtractor(BaseSectionExtractor):
    def __init__(self):
        super().__init__(CampaignHashtag, ["hashtag", "tags", "mention"])

class NoteExtractor(BaseSectionExtractor):
    """
    Fallback extractor that matches anything and produces CampaignNote.
    """
    def __init__(self):
        super().__init__(CampaignNote, [])
        
    def can_extract(self, section: DocumentSection) -> bool:
        # Notes are a fallback, usually this can_extract won't be called if orchestrated correctly
        # or we just return True for everything that wasn't matched.
        return True
