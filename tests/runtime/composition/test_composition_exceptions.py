import pytest
from backend.src.runtime.composition.composition_exceptions import (
    CompositionException,
    CompositionValidationException,
    CompositionBuildException,
    IncompleteCompositionException,
    CompositionFrozenException
)

def test_composition_exception_hierarchy():
    assert issubclass(CompositionValidationException, CompositionException)
    assert issubclass(CompositionBuildException, CompositionException)
    assert issubclass(IncompleteCompositionException, CompositionException)
    assert issubclass(CompositionFrozenException, CompositionException)

def test_composition_validation_exception():
    exc = CompositionValidationException("Validation failed")
    assert str(exc) == "Validation failed"
    with pytest.raises(CompositionValidationException):
        raise exc

def test_composition_build_exception():
    exc = CompositionBuildException("Build failed")
    assert str(exc) == "Build failed"
    with pytest.raises(CompositionBuildException):
        raise exc

def test_incomplete_composition_exception():
    exc = IncompleteCompositionException("Incomplete")
    assert str(exc) == "Incomplete"
    with pytest.raises(IncompleteCompositionException):
        raise exc

def test_composition_frozen_exception():
    exc = CompositionFrozenException("Frozen")
    assert str(exc) == "Frozen"
    with pytest.raises(CompositionFrozenException):
        raise exc
