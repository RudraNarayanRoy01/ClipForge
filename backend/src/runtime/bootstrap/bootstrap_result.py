"""
Bootstrap Result.

Canonical immutable boundary object for the Runtime Bootstrap phase.
Contains ONLY immutable artifacts, warnings, and errors.
"""
from dataclasses import dataclass
from typing import Tuple

from .runtime_bootstrap_composition import RuntimeBootstrapComposition
from .runtime_bootstrap_snapshot import RuntimeBootstrapSnapshot
from .runtime_bootstrap_statistics import RuntimeBootstrapStatistics
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .runtime_bootstrap import RuntimeBootstrap


@dataclass(frozen=True)
class BootstrapResult:
    """
    Immutable representation of the outcome of a Bootstrap Foundation build.
    Mirrors the architecture established in RuntimeServiceResult.
    Contains no execution state, provider state, or lifecycle state.
    """
    _bootstrap: 'RuntimeBootstrap'
    _composition: RuntimeBootstrapComposition
    _snapshot: RuntimeBootstrapSnapshot
    _statistics: RuntimeBootstrapStatistics
    _warnings: Tuple[str, ...]
    _errors: Tuple[str, ...]

    def __init__(
        self,
        bootstrap: 'RuntimeBootstrap',
        composition: RuntimeBootstrapComposition,
        snapshot: RuntimeBootstrapSnapshot,
        statistics: RuntimeBootstrapStatistics,
        warnings: Tuple[str, ...],
        errors: Tuple[str, ...]
    ):
        object.__setattr__(self, "_bootstrap", bootstrap)
        object.__setattr__(self, "_composition", composition)
        object.__setattr__(self, "_snapshot", snapshot)
        object.__setattr__(self, "_statistics", statistics)
        object.__setattr__(self, "_warnings", tuple(warnings))
        object.__setattr__(self, "_errors", tuple(errors))

    @property
    def bootstrap(self) -> 'RuntimeBootstrap':
        return self._bootstrap

    @property
    def composition(self) -> RuntimeBootstrapComposition:
        return self._composition

    @property
    def snapshot(self) -> RuntimeBootstrapSnapshot:
        return self._snapshot

    @property
    def statistics(self) -> RuntimeBootstrapStatistics:
        return self._statistics

    @property
    def warnings(self) -> Tuple[str, ...]:
        return self._warnings

    @property
    def errors(self) -> Tuple[str, ...]:
        return self._errors

    @property
    def is_success(self) -> bool:
        return len(self._errors) == 0
