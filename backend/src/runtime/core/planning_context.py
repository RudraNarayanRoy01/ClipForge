from dataclasses import dataclass, field
from typing import Tuple

@dataclass(frozen=True)
class PlanningContext:
    """
    Immutable representation of abstract planning preferences and constraints.

    This contract answers "What abstract planning preferences or constraints should be 
    considered when planning this intent?"

    It establishes the INPUT boundary for the ExecutionPlanner, completely separated 
    from WHAT work is requested (ExecutionIntent) and HOW the Runtime intends to 
    satisfy it (PlanningResult).

    It explicitly DOES NOT contain:
    - Provider information (e.g., openai, gemini)
    - Hardware/resource information (e.g., gpu, cuda)
    - Scheduling queues or priorities
    - Execution commands
    - Telemetry dumps

    Attributes:
        quality_preference: Abstract preference for quality (e.g., 'balanced', 'quality').
        latency_preference: Abstract preference for latency (e.g., 'standard', 'low').
        cost_preference: Abstract preference for cost (e.g., 'balanced', 'economy').
        locality_preference: Abstract preference for execution location (e.g., 'agnostic', 'local', 'remote').
        constraints: Generic abstract planning constraints. The frozen dataclass prevents
                     reassignment of top-level fields, and the constraints contract uses 
                     Tuple[str, ...], providing an immutable constraint collection under 
                     the declared type.
    """
    quality_preference: str = "balanced"
    latency_preference: str = "standard"
    cost_preference: str = "balanced"
    locality_preference: str = "agnostic"
    constraints: Tuple[str, ...] = field(default_factory=tuple)
