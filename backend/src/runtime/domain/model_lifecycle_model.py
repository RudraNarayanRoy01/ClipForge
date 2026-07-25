from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


class ModelLifecycleState(Enum):
    """
    Categorizes the current state of a model's lifecycle.
    Categorization only. No behavior.
    """
    REGISTERED = "REGISTERED"
    DOWNLOADING = "DOWNLOADING"
    INSTALLING = "INSTALLING"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    IDLE = "IDLE"
    BUSY = "BUSY"
    UPDATING = "UPDATING"
    DEPRECATED = "DEPRECATED"
    DISABLED = "DISABLED"
    REMOVED = "REMOVED"


@dataclass(frozen=True)
class ModelLifecycleTransition:
    """
    Metadata detailing a lifecycle transition.
    No transition logic.
    """
    from_state: ModelLifecycleState
    to_state: ModelLifecycleState
    transition_reason: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


# Centralized immutable transition policy owned by the Lifecycle Domain
MODEL_LIFECYCLE_TRANSITION_POLICY: Dict[ModelLifecycleState, List[ModelLifecycleState]] = {
    ModelLifecycleState.REGISTERED: [
        ModelLifecycleState.DOWNLOADING,
        ModelLifecycleState.INSTALLING,
        ModelLifecycleState.INITIALIZING,
        ModelLifecycleState.READY,
        ModelLifecycleState.REMOVED,
    ],
    ModelLifecycleState.DOWNLOADING: [
        ModelLifecycleState.INSTALLING,
        ModelLifecycleState.INITIALIZING,
        ModelLifecycleState.READY,
        ModelLifecycleState.REMOVED,
    ],
    ModelLifecycleState.INSTALLING: [
        ModelLifecycleState.INITIALIZING,
        ModelLifecycleState.READY,
        ModelLifecycleState.REMOVED,
    ],
    ModelLifecycleState.INITIALIZING: [
        ModelLifecycleState.READY,
        ModelLifecycleState.REMOVED,
    ],
    ModelLifecycleState.READY: [
        ModelLifecycleState.BUSY,
        ModelLifecycleState.IDLE,
        ModelLifecycleState.UPDATING,
        ModelLifecycleState.DEPRECATED,
        ModelLifecycleState.DISABLED,
        ModelLifecycleState.REMOVED,
    ],
    ModelLifecycleState.IDLE: [
        ModelLifecycleState.BUSY,
        ModelLifecycleState.READY,
        ModelLifecycleState.UPDATING,
        ModelLifecycleState.DEPRECATED,
        ModelLifecycleState.DISABLED,
        ModelLifecycleState.REMOVED,
    ],
    ModelLifecycleState.BUSY: [
        ModelLifecycleState.IDLE,
        ModelLifecycleState.READY,
        ModelLifecycleState.UPDATING,
    ],
    ModelLifecycleState.UPDATING: [
        ModelLifecycleState.READY,
        ModelLifecycleState.REMOVED,
    ],
    ModelLifecycleState.DEPRECATED: [
        ModelLifecycleState.DISABLED,
        ModelLifecycleState.REMOVED,
    ],
    ModelLifecycleState.DISABLED: [
        ModelLifecycleState.READY,
        ModelLifecycleState.REMOVED,
    ],
    ModelLifecycleState.REMOVED: [],
}


@dataclass(frozen=True)
class ModelLifecycleInfo:
    """
    Canonical immutable lifecycle metadata.
    References only `model_id`.
    Never embeds ModelInfo, ProviderInfo, or ProviderCapability.
    Passive metadata. No execution behavior.
    """
    model_id: str
    current_state: ModelLifecycleState
    previous_state: Optional[ModelLifecycleState] = None
    last_transition: Optional[ModelLifecycleTransition] = None
    transition_reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ModelLifecycleResult:
    """
    Immutable artifact returned by lifecycle operations.
    Contains `ModelLifecycleInfo`, operation summary, and validation result.
    No mutable state. No behavior.
    """
    lifecycle_info: ModelLifecycleInfo
    operation_summary: str
    validation_result: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)
