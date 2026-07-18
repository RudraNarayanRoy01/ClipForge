from dataclasses import dataclass
from enum import Enum

class CampaignSource(str, Enum):
    """
    Provenance of the campaign text. This is purely metadata and 
    does not affect the normalization behavior.
    """
    UNKNOWN = "UNKNOWN"
    DISCORD = "DISCORD"
    WHOP = "WHOP"
    CLIPSTER = "CLIPSTER"
    MARKDOWN = "MARKDOWN"
    PLAINTEXT = "PLAINTEXT"

@dataclass(frozen=True)
class NormalizedCampaignText:
    """
    Canonical representation of campaign text after deterministic normalization.
    This is an immutable object intended to be consumed by downstream 
    parsing and reasoning engines.
    """
    original_text: str
    normalized_text: str
    source: CampaignSource = CampaignSource.UNKNOWN
