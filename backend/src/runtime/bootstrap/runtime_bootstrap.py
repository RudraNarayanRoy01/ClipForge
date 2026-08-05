"""
Runtime Bootstrap.

Canonical minimal wrapper for the Bootstrap Foundation.
Owns ONLY identity, Descriptor, Composition, and State.
"""
from dataclasses import dataclass

from .runtime_bootstrap_descriptor import RuntimeBootstrapDescriptor
from .runtime_bootstrap_composition import RuntimeBootstrapComposition
from .runtime_bootstrap_state import RuntimeBootstrapState


@dataclass(frozen=True)
class RuntimeBootstrap:
    """
    Immutable representation of the canonical Runtime Bootstrap.
    
    Owns ONLY:
    - identifier
    - descriptor
    - composition
    - state
    
    Bootstrap is metadata only. Contains no computed behavior or utility methods.
    """
    _identifier: str
    _descriptor: RuntimeBootstrapDescriptor
    _composition: RuntimeBootstrapComposition
    _state: RuntimeBootstrapState

    def __init__(
        self,
        identifier: str,
        descriptor: RuntimeBootstrapDescriptor,
        composition: RuntimeBootstrapComposition,
        state: RuntimeBootstrapState
    ):
        object.__setattr__(self, "_identifier", identifier)
        object.__setattr__(self, "_descriptor", descriptor)
        object.__setattr__(self, "_composition", composition)
        object.__setattr__(self, "_state", state)

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def descriptor(self) -> RuntimeBootstrapDescriptor:
        return self._descriptor

    @property
    def composition(self) -> RuntimeBootstrapComposition:
        return self._composition

    @property
    def state(self) -> RuntimeBootstrapState:
        return self._state
