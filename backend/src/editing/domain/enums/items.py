from enum import Enum

class ScalingMode(str, Enum):
    FIT = "FIT"
    FILL = "FILL"
    STRETCH = "STRETCH"

class TimelineItemType(str, Enum):
    CLIP = "CLIP"
    SUBTITLE = "SUBTITLE"
    OVERLAY = "OVERLAY"
    TRANSITION = "TRANSITION"
