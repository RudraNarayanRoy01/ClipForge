from enum import Enum

class EditOperation(Enum):
    """
    Strongly typed enum for editing operations representing editorial intent.
    """
    CUT = "CUT"
    TRIM = "TRIM"
    TRANSITION = "TRANSITION"
    ZOOM = "ZOOM"
    OVERLAY = "OVERLAY"
    SPEED = "SPEED"
    SUBTITLE = "SUBTITLE"
    AUDIO = "AUDIO"
    HIGHLIGHT = "HIGHLIGHT"

class EditTarget(Enum):
    """
    Strongly typed enum describing what a decision applies to.
    """
    PROJECT = "PROJECT"
    TIMELINE = "TIMELINE"
    CLIP = "CLIP"
    SUBTITLE = "SUBTITLE"
    AUDIO = "AUDIO"
