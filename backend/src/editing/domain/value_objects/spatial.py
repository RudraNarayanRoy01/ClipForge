from dataclasses import dataclass

@dataclass(frozen=True)
class Position:
    """
    X, Y coordinates.
    """
    x: float
    y: float

@dataclass(frozen=True)
class Size:
    """
    Width, Height.
    """
    width: float
    height: float

@dataclass(frozen=True)
class BoundingBox:
    """
    Origin position and size.
    """
    origin: Position
    size: Size

@dataclass(frozen=True)
class VideoResolution:
    """
    Video resolution with width and height.
    """
    width: int
    height: int
