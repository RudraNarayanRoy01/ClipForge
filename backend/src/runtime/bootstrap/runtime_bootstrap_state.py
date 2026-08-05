"""
Runtime Bootstrap State.

Canonical immutable wrapper for the Bootstrap Stage.
"""
from dataclasses import dataclass

from .bootstrap_stage import BootstrapStage


@dataclass(frozen=True)
class RuntimeBootstrapState:
    """
    Immutable representation of the current state of a Runtime Bootstrap.
    References canonical BootstrapStage.
    """
    _stage: BootstrapStage

    def __init__(self, stage: BootstrapStage):
        object.__setattr__(self, "_stage", stage)

    @property
    def stage(self) -> BootstrapStage:
        return self._stage
