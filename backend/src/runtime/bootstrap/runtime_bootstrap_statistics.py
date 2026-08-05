"""
Runtime Bootstrap Statistics.

Canonical immutable representation of bootstrap planning metrics.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeBootstrapStatistics:
    """
    Immutable representation of bootstrap planning statistics.
    Contains ONLY declarative planning metrics, entirely separate from topology.
    """
    _layer_count: int
    _dependency_batch_count: int
    _planned_initialization_steps: int
    _descriptor_count: int
    _bootstrap_group_count: int
    _planning_depth: int

    def __init__(
        self,
        layer_count: int,
        dependency_batch_count: int,
        planned_initialization_steps: int,
        descriptor_count: int,
        bootstrap_group_count: int,
        planning_depth: int
    ):
        object.__setattr__(self, "_layer_count", layer_count)
        object.__setattr__(self, "_dependency_batch_count", dependency_batch_count)
        object.__setattr__(self, "_planned_initialization_steps", planned_initialization_steps)
        object.__setattr__(self, "_descriptor_count", descriptor_count)
        object.__setattr__(self, "_bootstrap_group_count", bootstrap_group_count)
        object.__setattr__(self, "_planning_depth", planning_depth)

    @property
    def layer_count(self) -> int:
        return self._layer_count

    @property
    def dependency_batch_count(self) -> int:
        return self._dependency_batch_count

    @property
    def planned_initialization_steps(self) -> int:
        return self._planned_initialization_steps
        
    @property
    def descriptor_count(self) -> int:
        return self._descriptor_count
        
    @property
    def bootstrap_group_count(self) -> int:
        return self._bootstrap_group_count
        
    @property
    def planning_depth(self) -> int:
        return self._planning_depth
