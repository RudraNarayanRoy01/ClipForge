from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class EntitySourceReference:
    """
    Lightweight source traceability information.
    Preserves connection to original parsing locations without 
    depending directly on parsing models.
    """
    section_position: int
    element_index: int
    start_line: int
    end_line: int

@dataclass(frozen=True)
class CampaignEntity:
    """
    Immutable base class for all extracted business entities.
    """
    original_text: str
    source_reference: EntitySourceReference

@dataclass(frozen=True)
class CampaignRequirement(CampaignEntity):
    """An explicit requirement for the campaign (e.g., follower count, content type)."""
    pass

@dataclass(frozen=True)
class CampaignRestriction(CampaignEntity):
    """An explicit restriction for the campaign (e.g., no other brands)."""
    pass

@dataclass(frozen=True)
class CampaignPlatform(CampaignEntity):
    """A target platform for the campaign (e.g., TikTok, Instagram)."""
    pass

@dataclass(frozen=True)
class CampaignRegion(CampaignEntity):
    """A target region or geography for the campaign."""
    pass

@dataclass(frozen=True)
class CampaignReward(CampaignEntity):
    """A reward, payout, or compensation related to the campaign."""
    pass

@dataclass(frozen=True)
class CampaignDeadline(CampaignEntity):
    """A specific deadline or timeline for the campaign."""
    pass

@dataclass(frozen=True)
class CampaignDeliverable(CampaignEntity):
    """A specific deliverable expected from the creator."""
    pass

@dataclass(frozen=True)
class CampaignAudioRule(CampaignEntity):
    """An audio or music related rule."""
    pass

@dataclass(frozen=True)
class CampaignHashtag(CampaignEntity):
    """A hashtag that must be included in the campaign."""
    pass

@dataclass(frozen=True)
class CampaignNote(CampaignEntity):
    """A generic or unrecognized campaign detail. Used for unknown content."""
    pass

@dataclass(frozen=True)
class CampaignEntityDocument:
    """
    The extracted deterministic business entities.
    Aggregates typed entities extracted from a structured document.
    """
    requirements: List[CampaignRequirement] = field(default_factory=list)
    restrictions: List[CampaignRestriction] = field(default_factory=list)
    platforms: List[CampaignPlatform] = field(default_factory=list)
    regions: List[CampaignRegion] = field(default_factory=list)
    rewards: List[CampaignReward] = field(default_factory=list)
    deadlines: List[CampaignDeadline] = field(default_factory=list)
    deliverables: List[CampaignDeliverable] = field(default_factory=list)
    audio_rules: List[CampaignAudioRule] = field(default_factory=list)
    hashtags: List[CampaignHashtag] = field(default_factory=list)
    notes: List[CampaignNote] = field(default_factory=list)
