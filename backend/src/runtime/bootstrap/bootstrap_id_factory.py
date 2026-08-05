"""
Bootstrap ID Factory.

Strict SRP factory for generating unique deterministic identifiers.
"""
import uuid


class BootstrapIdFactory:
    """
    Factory dedicated exclusively to generating deterministic and 
    unique identifiers for Runtime Bootstrap components.
    """

    def generate_composition_id(self) -> str:
        """Generates a unique identifier for a Bootstrap Composition."""
        return f"bootstrap_comp_{uuid.uuid4().hex[:12]}"

    def generate_runtime_bootstrap_id(self) -> str:
        """Generates a unique identifier for a Runtime Bootstrap."""
        return f"runtime_bootstrap_{uuid.uuid4().hex[:12]}"
