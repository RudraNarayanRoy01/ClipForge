"""
Runtime Bootstrap Factory.

Strict SRP factory for assembling the final canonical Runtime Bootstrap wrapper.
"""
from .runtime_bootstrap_descriptor import RuntimeBootstrapDescriptor
from .runtime_bootstrap_composition import RuntimeBootstrapComposition
from .runtime_bootstrap_state import RuntimeBootstrapState
from .bootstrap_stage import BootstrapStage
from .runtime_bootstrap import RuntimeBootstrap


class RuntimeBootstrapFactory:
    """
    Factory dedicated exclusively to constructing the RuntimeBootstrap canonical wrapper.
    """

    def build_bootstrap(
        self,
        bootstrap_id: str,
        descriptor: RuntimeBootstrapDescriptor,
        composition: RuntimeBootstrapComposition
    ) -> RuntimeBootstrap:
        """Constructs the canonical RuntimeBootstrap instance."""
        state = RuntimeBootstrapState(stage=BootstrapStage.READY)
        
        return RuntimeBootstrap(
            identifier=bootstrap_id,
            descriptor=descriptor,
            composition=composition,
            state=state
        )
