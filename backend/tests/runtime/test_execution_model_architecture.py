import inspect
import dataclasses
from src.runtime.core.execution_model import (
    ExecutionIdentity,
    ExecutionRequest,
    ExecutionStatus,
    ExecutionResult,
)


def test_execution_identity_is_immutable():
    """Verify ExecutionIdentity is a frozen dataclass."""
    assert dataclasses.is_dataclass(ExecutionIdentity)
    # Check if frozen
    assert ExecutionIdentity.__dataclass_params__.frozen is True


def test_execution_request_is_immutable():
    """Verify ExecutionRequest is a frozen dataclass."""
    assert dataclasses.is_dataclass(ExecutionRequest)
    assert ExecutionRequest.__dataclass_params__.frozen is True


def test_execution_status_is_immutable():
    """Verify ExecutionStatus is a frozen dataclass."""
    assert dataclasses.is_dataclass(ExecutionStatus)
    assert ExecutionStatus.__dataclass_params__.frozen is True


def test_execution_result_is_immutable():
    """Verify ExecutionResult is a frozen dataclass."""
    assert dataclasses.is_dataclass(ExecutionResult)
    assert ExecutionResult.__dataclass_params__.frozen is True


def test_no_execution_methods():
    """
    Verify that none of the execution domain models contain logic methods
    (like transition(), schedule(), execute(), calculate_progress()).
    They should only be data structures.
    """
    artifacts = [ExecutionIdentity, ExecutionRequest, ExecutionStatus, ExecutionResult]
    
    for artifact_class in artifacts:
        # Get all methods defined in the class (excluding inherited ones like __init__ from dataclass, etc)
        methods = [
            m for m in dir(artifact_class) 
            if callable(getattr(artifact_class, m)) and not m.startswith("__")
        ]
        assert len(methods) == 0, f"{artifact_class.__name__} should not have logic methods, found: {methods}"


def test_identity_not_containing_correlation():
    """Verify ExecutionIdentity does not contain correlation_id."""
    fields = {f.name for f in dataclasses.fields(ExecutionIdentity)}
    assert "execution_id" in fields
    assert "created_at" in fields
    assert "correlation_id" not in fields, "Correlation ID should not be in ExecutionIdentity."


def test_dependency_integrity():
    """Verify ExecutionRequest, ExecutionStatus, and ExecutionResult contain ExecutionIdentity."""
    request_fields = {f.name: f.type for f in dataclasses.fields(ExecutionRequest)}
    assert "identity" in request_fields
    assert request_fields["identity"] == ExecutionIdentity or request_fields["identity"] == 'ExecutionIdentity'

    status_fields = {f.name: f.type for f in dataclasses.fields(ExecutionStatus)}
    assert "identity" in status_fields
    
    result_fields = {f.name: f.type for f in dataclasses.fields(ExecutionResult)}
    assert "identity" in result_fields
