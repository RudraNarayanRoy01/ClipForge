from enum import Enum

class TransitionType(str, Enum):
    CROSS_DISSOLVE = "CROSS_DISSOLVE"
    WIPE = "WIPE"
    FADE_TO_BLACK = "FADE_TO_BLACK"
