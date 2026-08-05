"""
Bootstrap Stage.

Canonical immutable representations of Runtime Bootstrap stages.
Contains only metadata states, zero execution logic.
"""
from enum import Enum


class BootstrapStage(Enum):
    """
    Immutable canonical bootstrap stages.
    These stages describe what the Runtime Bootstrap has achieved observationally.
    They DO NOT represent execution (e.g., RUNNING, STOPPED, FAILED).
    """
    UNINITIALIZED = "UNINITIALIZED"
    PREPARED = "PREPARED"
    VALIDATED = "VALIDATED"
    READY = "READY"
