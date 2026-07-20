from enum import Enum

class TrackType(str, Enum):
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    SUBTITLE = "SUBTITLE"
    OVERLAY = "OVERLAY"
    EFFECT = "EFFECT"

class TimelineTrackType(str, Enum):
    """Categories of tracks within the editable timeline state."""
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    OVERLAY = "OVERLAY"
    SUBTITLE = "SUBTITLE"
