"""
Injection ID Factory.

SRP-compliant factory for generating deterministic or unique IDs for injection compositions.
"""
import uuid


class InjectionIdFactory:
    """Creates deterministic or unique IDs for injection compositions."""
    
    def create(self) -> str:
        """Generates a unique composition identifier."""
        return f"composition-{uuid.uuid4().hex}"
