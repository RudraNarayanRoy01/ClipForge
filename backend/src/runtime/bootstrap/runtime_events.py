import datetime
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass(frozen=True)
class RuntimeEvent:
    """Base class for structured Runtime lifecycle events."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    runtime_identifier: str = ""


@dataclass(frozen=True)
class RuntimeCreated(RuntimeEvent):
    """Generated when the Runtime is initially instantiated and configured."""
    configuration_summary: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BootstrapStarted(RuntimeEvent):
    """Generated when the bootstrap process commences."""
    pass


@dataclass(frozen=True)
class InitializationStarted(RuntimeEvent):
    """Generated when the initialization stages of the bootstrap pipeline begin."""
    pass


@dataclass(frozen=True)
class ValidationStarted(RuntimeEvent):
    """Generated when the validation stages of the bootstrap pipeline begin."""
    pass


@dataclass(frozen=True)
class RuntimeReady(RuntimeEvent):
    """Generated when the bootstrap sequence completes successfully and the Runtime is READY."""
    duration: float = 0.0
    initialized_components: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ShutdownStarted(RuntimeEvent):
    """Generated when a safe shutdown sequence is initiated."""
    pass


@dataclass(frozen=True)
class RuntimeStopped(RuntimeEvent):
    """Generated when the Runtime safely transitions to the STOPPED state."""
    pass


@dataclass(frozen=True)
class BootstrapFailed(RuntimeEvent):
    """Generated when an unrecoverable failure forces the Runtime into the FAILED state."""
    reason: str = ""
    state: str = ""
    diagnostics: Dict[str, Any] = field(default_factory=dict)
