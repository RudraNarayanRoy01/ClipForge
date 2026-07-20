from enum import Enum

class Orientation(str, Enum):
    PORTRAIT = "PORTRAIT"
    LANDSCAPE = "LANDSCAPE"
    SQUARE = "SQUARE"

class ExportQuality(str, Enum):
    LOW = "LOW"
    BALANCED = "BALANCED"
    HIGH = "HIGH"
    LOSSLESS = "LOSSLESS"
