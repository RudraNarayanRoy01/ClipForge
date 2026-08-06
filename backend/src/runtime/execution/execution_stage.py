from enum import Enum, auto

class ExecutionStage(Enum):
    UNINITIALIZED = auto()
    PREPARED = auto()
    VALIDATED = auto()
    READY = auto()
