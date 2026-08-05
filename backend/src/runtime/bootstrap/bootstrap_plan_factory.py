"""
Bootstrap Plan Factory.

Strict SRP factory for constructing the RuntimeBootstrapPlan.
Contains zero validation, orchestration, or metadata generation.
"""
from typing import List

from .runtime_bootstrap_layer import RuntimeBootstrapLayer
from .runtime_bootstrap_plan import RuntimeBootstrapPlan


class BootstrapPlanFactory:
    """
    Factory dedicated exclusively to constructing the immutable RuntimeBootstrapPlan.
    """

    def build_plan(self, layers: List[RuntimeBootstrapLayer]) -> RuntimeBootstrapPlan:
        """Constructs the canonical RuntimeBootstrapPlan from an ordered list of layers."""
        return RuntimeBootstrapPlan(layers=tuple(layers))
