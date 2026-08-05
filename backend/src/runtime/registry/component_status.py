from enum import Enum, auto

class RuntimeComponentStatus(Enum):
    """
    Defines the metadata status of a Runtime Component.
    
    This is pure metadata. Do NOT confuse this with RuntimeState which represents the
    lifecycle of the runtime itself.
    """
    REGISTERED = auto()
    AVAILABLE = auto()
    DISABLED = auto()
    DEPRECATED = auto()
    UNKNOWN = auto()
