import pytest

from backend.src.runtime.bootstrap.runtime_state import RuntimeState
from backend.src.runtime.bootstrap.bootstrap_configuration import BootstrapConfiguration
from backend.src.runtime.bootstrap.bootstrap_exceptions import (
    RuntimeBootstrapException,
    BootstrapInitializationException,
    BootstrapValidationException,
    BootstrapShutdownException,
    InvalidRuntimeStateTransitionException,
)
from backend.src.runtime.bootstrap.bootstrap_pipeline import BootstrapPipeline
from backend.src.runtime.bootstrap.runtime_bootstrap import RuntimeBootstrap


def test_successful_bootstrap():
    bootstrap = RuntimeBootstrap()
    assert bootstrap.state() == RuntimeState.CREATED
    
    result = bootstrap.bootstrap()
    
    assert result.success is True
    assert result.runtime_state == RuntimeState.READY
    assert bootstrap.state() == RuntimeState.READY
    assert result.duration >= 0
    assert "BootstrapContext" in result.initialized_components

def test_successful_shutdown():
    bootstrap = RuntimeBootstrap()
    bootstrap.bootstrap()
    
    bootstrap.shutdown()
    assert bootstrap.state() == RuntimeState.STOPPED

def test_successful_restart():
    bootstrap = RuntimeBootstrap()
    bootstrap.bootstrap()
    
    # Restart from READY
    result = bootstrap.restart()
    assert result.success is True
    assert bootstrap.state() == RuntimeState.READY

def test_illegal_state_transition():
    bootstrap = RuntimeBootstrap()
    
    with pytest.raises(InvalidRuntimeStateTransitionException) as excinfo:
        # Cannot shutdown from CREATED
        bootstrap.shutdown()
        
    assert excinfo.value.current_state == RuntimeState.CREATED
    assert excinfo.value.attempted_state == RuntimeState.SHUTTING_DOWN
    
    # State should be preserved on illegal transition
    assert bootstrap.state() == RuntimeState.CREATED

def test_bootstrap_initialization_failure():
    from backend.src.runtime.bootstrap.bootstrap_pipeline import BootstrapStage
    
    class FaultyStage(BootstrapStage):
        def execute(self, context):
            raise Exception("Faulty init")
            
    bootstrap = RuntimeBootstrap()
    bootstrap._pipeline.register_initialization_stage(FaultyStage())
    
    with pytest.raises(BootstrapInitializationException):
        bootstrap.bootstrap()
        
    assert bootstrap.state() == RuntimeState.FAILED

def test_bootstrap_validation_failure():
    from backend.src.runtime.bootstrap.bootstrap_pipeline import BootstrapStage
    
    class FaultyValidationStage(BootstrapStage):
        def execute(self, context):
            raise Exception("Faulty validation")
            
    bootstrap = RuntimeBootstrap()
    bootstrap._pipeline.register_validation_stage(FaultyValidationStage())
    
    with pytest.raises(BootstrapValidationException):
        bootstrap.bootstrap()
        
    assert bootstrap.state() == RuntimeState.FAILED

def test_restart_from_stopped():
    bootstrap = RuntimeBootstrap()
    bootstrap.bootstrap()
    bootstrap.shutdown()
    assert bootstrap.state() == RuntimeState.STOPPED
    
    result = bootstrap.restart()
    assert result.success is True
    assert bootstrap.state() == RuntimeState.READY

def test_restart_from_failed():
    from backend.src.runtime.bootstrap.bootstrap_pipeline import BootstrapStage
    class FaultyStage(BootstrapStage):
        def execute(self, context):
            raise Exception("Faulty init")

    bootstrap = RuntimeBootstrap()
    bootstrap._pipeline.register_initialization_stage(FaultyStage())
    
    try:
        bootstrap.bootstrap()
    except Exception:
        pass
    
    assert bootstrap.state() == RuntimeState.FAILED
    
    # Restore normal pipeline for restart
    from backend.src.runtime.bootstrap.bootstrap_pipeline import BootstrapPipeline
    bootstrap._pipeline = BootstrapPipeline()
    result = bootstrap.restart()
    assert result.success is True
    assert bootstrap.state() == RuntimeState.READY
