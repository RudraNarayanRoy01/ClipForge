"""
Factory for Service Composition identifiers.
"""
import uuid

class ServiceIdFactory:
    """Creates isolated composition identifiers."""
    
    @staticmethod
    def create_id() -> str:
        return f"svc_comp_{uuid.uuid4().hex[:12]}"
