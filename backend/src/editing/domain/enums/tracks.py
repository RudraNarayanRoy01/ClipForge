from enum import Enum

class TrackType(str, Enum):
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    SUBTITLE = "SUBTITLE"
    OVERLAY = "OVERLAY"
    EFFECT = "EFFECT"
