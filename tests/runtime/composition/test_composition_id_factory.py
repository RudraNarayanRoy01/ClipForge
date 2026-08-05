import pytest
from backend.src.runtime.composition.composition_id_factory import CompositionIdFactory
import uuid

def test_generate_id():
    id1 = CompositionIdFactory.generate_id()
    id2 = CompositionIdFactory.generate_id()
    
    assert id1 != id2
    
    # Validates it's a UUID string
    assert isinstance(uuid.UUID(id1), uuid.UUID)
