from enum import Enum, auto

class RuntimeComponentType(Enum):
    """
    Defines the fundamental type of a Runtime Component.
    
    This is pure metadata and does not imply any specific execution or dependency behavior.
    """
    CORE = auto()
    BOOTSTRAP = auto()
    REGISTRY = auto()
    EXECUTION = auto()
    PROVIDER = auto()
    POLICY = auto()
    MONITORING = auto()
    TELEMETRY = auto()
    SCHEDULER = auto()
    UNKNOWN = auto()
