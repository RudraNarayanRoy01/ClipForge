from dataclasses import dataclass

@dataclass(frozen=True)
class Time:
    """
    Abstract representation of time.
    Currently encapsulates a float in seconds, designed for future migration
    to Rational/SMPTE timecode without breaking models.
    """
    value: float

@dataclass(frozen=True)
class TimeRange:
    """
    Represents a duration with start and end times.
    """
    start: Time
    end: Time
