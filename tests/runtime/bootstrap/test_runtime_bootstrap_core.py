import pytest
from datetime import datetime, timezone

from backend.src.runtime.bootstrap.runtime_state import RuntimeState
from backend.src.runtime.bootstrap.bootstrap_configuration import BootstrapConfiguration
from backend.src.runtime.bootstrap.bootstrap_context import BootstrapContext
from backend.src.runtime.bootstrap.bootstrap_result import BootstrapResult
from backend.src.runtime.bootstrap.bootstrap_exceptions import (
    RuntimeBootstrapException,
    BootstrapInitializationException,
    BootstrapValidationException,
    BootstrapShutdownException,
    InvalidRuntimeStateTransitionException,
)

def test_runtime_state_enum():
    assert RuntimeState.CREATED.name == "CREATED"
    assert RuntimeState.BOOTSTRAPPING.name == "BOOTSTRAPPING"
    assert RuntimeState.READY.name == "READY"
    assert len(RuntimeState) == 8

def test_bootstrap_configuration_defaults():
    config = BootstrapConfiguration()
    assert config.startup_timeout == 30.0
    assert config.diagnostics_enabled is False
    assert config.validation_enabled is True
    assert config.startup_logging is True
    assert config.strict_bootstrap_mode is True

def test_bootstrap_context_initialization():
    config = BootstrapConfiguration(startup_timeout=10.0)
    context = BootstrapContext(configuration=config)
    
    assert context.runtime_identifier is not None
    assert isinstance(context.startup_timestamp, datetime)
    assert context.configuration.startup_timeout == 10.0
    assert context.environment == {}
    assert context.bootstrap_metadata == {}
    assert context.execution_context == {}

def test_bootstrap_result_immutability():
    result = BootstrapResult(
        success=True,
        runtime_state=RuntimeState.READY,
        duration=1.5
    )
    
    assert result.success is True
    assert result.runtime_state == RuntimeState.READY
    assert result.duration == 1.5
    
    with pytest.raises(Exception):
        # dataclasses frozen=True raises dataclasses.FrozenInstanceError
        result.success = False

def test_invalid_runtime_state_transition_exception():
    exc = InvalidRuntimeStateTransitionException(RuntimeState.CREATED, RuntimeState.READY)
    assert exc.current_state == RuntimeState.CREATED
    assert exc.attempted_state == RuntimeState.READY
    assert exc.state == RuntimeState.CREATED
    assert exc.reason == "Invalid state transition"
    assert "Illegal Runtime state transition from CREATED to READY" in str(exc)
