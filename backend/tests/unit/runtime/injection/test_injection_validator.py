import pytest
from backend.src.runtime.injection.injection_validator import InjectionValidator
from backend.src.runtime.injection.runtime_injection_binding import RuntimeInjectionBinding
from backend.src.runtime.injection.injection_descriptor import InjectionDescriptor
from backend.src.runtime.injection.injection_exceptions import (
    DuplicateBindingException,
    CircularInjectionException,
    MissingImplementationException,
    InvalidInjectionException
)


def test_validator_detects_duplicates():
    validator = InjectionValidator()
    bindings = (
        RuntimeInjectionBinding("I1", "Impl1", "s1", "SINGLETON", "GLOBAL"),
        RuntimeInjectionBinding("I1", "Impl2", "s2", "SINGLETON", "GLOBAL"),
    )
    with pytest.raises(DuplicateBindingException):
        validator.validate_bindings(bindings)

def test_validator_passes_valid_bindings():
    validator = InjectionValidator()
    bindings = (
        RuntimeInjectionBinding("I1", "Impl1", "s1", "SINGLETON", "GLOBAL"),
        RuntimeInjectionBinding("I2", "Impl2", "s2", "SINGLETON", "GLOBAL"),
    )
    validator.validate_bindings(bindings)

def test_validator_detects_missing_implementation():
    validator = InjectionValidator()
    bindings = (
        RuntimeInjectionBinding("I1", "Impl1", "s1", "SINGLETON", "GLOBAL"),
    )
    graph = {
        "I1": (InjectionDescriptor("REQ", False, "CTOR", "G", "I1", "I2"),)
    }
    with pytest.raises(MissingImplementationException):
        validator.validate_graph(bindings, graph)

def test_validator_allows_missing_optional_implementation():
    validator = InjectionValidator()
    bindings = (
        RuntimeInjectionBinding("I1", "Impl1", "s1", "SINGLETON", "GLOBAL"),
    )
    graph = {
        "I1": (InjectionDescriptor("REQ", True, "CTOR", "G", "I1", "I2"),)
    }
    validator.validate_graph(bindings, graph)

def test_validator_detects_circular_dependencies():
    validator = InjectionValidator()
    bindings = (
        RuntimeInjectionBinding("I1", "Impl1", "s1", "SINGLETON", "GLOBAL"),
        RuntimeInjectionBinding("I2", "Impl2", "s2", "SINGLETON", "GLOBAL"),
    )
    graph = {
        "I1": (InjectionDescriptor("REQ", False, "CTOR", "G", "I1", "I2"),),
        "I2": (InjectionDescriptor("REQ", False, "CTOR", "G", "I2", "I1"),)
    }
    with pytest.raises(CircularInjectionException):
        validator.validate_graph(bindings, graph)

def test_validator_invalid_types():
    validator = InjectionValidator()
    with pytest.raises(InvalidInjectionException):
        validator.validate_bindings([RuntimeInjectionBinding("I1", "Impl1", "s1", "S", "G")]) # list instead of tuple
