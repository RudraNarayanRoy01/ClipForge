import pytest
from src.runtime.bootstrap.runtime_bootstrap_builder import RuntimeBootstrapBuilder
from src.runtime.bootstrap.runtime_bootstrap_descriptor import RuntimeBootstrapDescriptor


def test_builder_pipeline_ordering():
    builder = RuntimeBootstrapBuilder()
    
    descriptor = RuntimeBootstrapDescriptor("test", "1.0", ())
    
    result = builder.build(
        descriptor=descriptor,
        descriptors={"test": descriptor},
        layers=[], # This should trigger validation failure
        adjacency={"test": set()}
    )
    
    assert not result.is_success
    assert len(result.errors) > 0
    assert "At least one RuntimeBootstrapLayer is required." in result.errors[0]
