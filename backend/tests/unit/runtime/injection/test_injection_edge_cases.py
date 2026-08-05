import pytest
from backend.src.runtime.injection.injection_validator import InjectionValidator
from backend.src.runtime.injection.runtime_injection_binding import RuntimeInjectionBinding
from backend.src.runtime.injection.injection_descriptor import InjectionDescriptor
from backend.src.runtime.injection.injection_exceptions import InvalidInjectionException
from backend.src.runtime.injection.injection_statistics_builder import InjectionStatisticsBuilder


def test_empty_graph_statistics():
    builder = InjectionStatisticsBuilder()
    stats = builder.build(tuple(), {})
    assert stats.binding_count == 0
    assert stats.graph_statistics.root_count == 0
    assert stats.graph_statistics.leaf_count == 0
    assert stats.graph_statistics.graph_depth == 0
    assert stats.graph_statistics.average_degree == 0.0
    assert stats.graph_statistics.connected_components == 0

def test_invalid_binding_properties():
    validator = InjectionValidator()
    with pytest.raises(InvalidInjectionException):
        validator.validate_bindings((RuntimeInjectionBinding("", "", "", "", ""),))

def test_invalid_graph_types():
    validator = InjectionValidator()
    bindings = (RuntimeInjectionBinding("I", "Impl", "s", "S", "G"),)
    
    with pytest.raises(InvalidInjectionException):
        validator.validate_graph(bindings, []) # not a mapping

    with pytest.raises(InvalidInjectionException):
        validator.validate_graph(bindings, {"I": "not a tuple"})
        
    with pytest.raises(InvalidInjectionException):
        validator.validate_graph(bindings, {"I": ("not a descriptor",)})
        
def test_invalid_binding_tuple():
    validator = InjectionValidator()
    with pytest.raises(InvalidInjectionException):
        validator.validate_bindings(["not a tuple"])
