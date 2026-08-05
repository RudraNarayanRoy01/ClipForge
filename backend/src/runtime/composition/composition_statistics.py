from dataclasses import dataclass

@dataclass(frozen=True)
class CompositionStatistics:
    """
    Statistics for a Runtime Composition.
    Observational only. No evaluation.
    """
    component_count: int
    dependency_count: int
    root_count: int
    leaf_count: int
    disconnected_count: int
