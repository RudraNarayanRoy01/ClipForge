import uuid

class CompositionIdFactory:
    """
    Factory for generating unique Composition identifiers.
    
    Responsibilities:
    - Generate Composition IDs
    - Isolate identifier generation
    - Prepare future extensibility
    """
    
    @staticmethod
    def generate_id() -> str:
        """
        Generates a unique identifier for a Runtime Composition.
        Returns a string representation of a UUID.
        """
        return str(uuid.uuid4())
