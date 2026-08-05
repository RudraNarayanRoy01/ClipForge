"""
Runtime Bootstrap Plan.

Canonical immutable representation of bootstrap ordering.
Contains zero execution, zero scheduling, and zero provider knowledge.
"""
from dataclasses import dataclass
from typing import Tuple

from .runtime_bootstrap_layer import RuntimeBootstrapLayer


@dataclass(frozen=True)
class RuntimeBootstrapPlan:
    """
    Immutable representation of the canonical Runtime Bootstrap Plan.
    
    Owns ONLY:
    - layers
    - dependency batches
    - ordering
    
    Nothing else.
    No execution. No lifecycle. No provider awareness. No scheduler. No activation.
    """
    _layers: Tuple[RuntimeBootstrapLayer, ...]

    def __init__(self, layers: Tuple[RuntimeBootstrapLayer, ...]):
        object.__setattr__(self, "_layers", tuple(layers))

    @property
    def layers(self) -> Tuple[RuntimeBootstrapLayer, ...]:
        return self._layers
