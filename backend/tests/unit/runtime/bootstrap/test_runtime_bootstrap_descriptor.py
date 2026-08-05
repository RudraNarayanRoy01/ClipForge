import pytest
from src.runtime.bootstrap.runtime_bootstrap_descriptor import RuntimeBootstrapDescriptor


def test_descriptor_immutability():
    descriptor = RuntimeBootstrapDescriptor("test_1", "1.0", ("dep_1",))
    
    with pytest.raises(AttributeError):
        descriptor.identifier = "test_2" # type: ignore
        
    with pytest.raises(AttributeError):
        descriptor.version = "2.0" # type: ignore
        
    with pytest.raises(AttributeError):
        descriptor.dependency_identifiers = () # type: ignore

def test_descriptor_equality():
    desc1 = RuntimeBootstrapDescriptor("test_1", "1.0", ("dep_1",))
    desc2 = RuntimeBootstrapDescriptor("test_1", "1.0", ("dep_1",))
    desc3 = RuntimeBootstrapDescriptor("test_2", "1.0", ("dep_1",))
    
    assert desc1 == desc2
    assert desc1 != desc3
    assert hash(desc1) == hash(desc2)

def test_descriptor_tuple_coercion():
    # Even if passed a list, it should store a tuple
    desc = RuntimeBootstrapDescriptor("test_1", "1.0", ["dep_1", "dep_2"]) # type: ignore
    assert isinstance(desc.dependency_identifiers, tuple)
    assert desc.dependency_identifiers == ("dep_1", "dep_2")

def test_descriptor_metadata_isolation():
    # Ensure descriptor does not have arbitrary metadata fields
    desc = RuntimeBootstrapDescriptor("test_1", "1.0", ())
    with pytest.raises(AttributeError):
        desc.labels # type: ignore
