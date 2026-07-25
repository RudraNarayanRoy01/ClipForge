import inspect
import ast
import sys
from pathlib import Path

# Add backend/src to sys.path so we can import runtime
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend" / "src"))

from runtime.domain.runtime_schedule_model import (
    RuntimeScheduleState,
    RuntimeScheduleTrigger,
    RuntimeScheduleDecision,
    RuntimeScheduleInfo,
    RuntimeScheduleResult,
    RUNTIME_SCHEDULE_POLICY
)
from runtime.core.runtime_scheduling_manager import RuntimeSchedulingManager
from runtime.core.context import RuntimeContext


def test_schedule_info_immutability():
    """Verify RuntimeScheduleInfo is immutable and doesn't own upstream objects."""
    import dataclasses
    
    # Must be frozen
    assert dataclasses.is_dataclass(RuntimeScheduleInfo)
    assert RuntimeScheduleInfo.__dataclass_params__.frozen is True
    
    # Must not own ProviderInfo, ProviderCapability, etc.
    fields = {f.name: f.type for f in dataclasses.fields(RuntimeScheduleInfo)}
    assert 'provider_info' not in fields
    assert 'capability' not in fields
    assert 'provider_health' not in fields
    assert 'provider_failover' not in fields
    assert 'runtime_retry' not in fields


def test_schedule_policy_immutability():
    """Verify RUNTIME_SCHEDULE_POLICY is a single source of truth and mapping is correct."""
    assert isinstance(RUNTIME_SCHEDULE_POLICY, dict)
    assert RuntimeScheduleTrigger.RETRY_READY in RUNTIME_SCHEDULE_POLICY
    assert RUNTIME_SCHEDULE_POLICY[RuntimeScheduleTrigger.RETRY_READY] == RuntimeScheduleState.READY
    
    # Ensure it doesn't map RuntimeRetryState directly
    from runtime.domain.runtime_retry_model import RuntimeRetryState
    assert RuntimeRetryState.ELIGIBLE not in RUNTIME_SCHEDULE_POLICY


def test_scheduling_manager_imports():
    """
    Verify RuntimeSchedulingManager does not import execution engines,
    temporal scheduling libraries, or networking components.
    """
    manager_file = Path(inspect.getfile(RuntimeSchedulingManager))
    tree = ast.parse(manager_file.read_text())
    
    forbidden_imports = {
        'asyncio', 'threading', 'time', 'sched', 'APScheduler',
        'http', 'requests', 'urllib', 'aiohttp', 'httpx',
        'runtime_executor', 'runtime_scheduler_engine'
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in forbidden_imports, f"Forbidden import found: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                assert node.module not in forbidden_imports, f"Forbidden from-import found: {node.module}"


def test_context_passive_composition():
    """Verify RuntimeContext instantiates and exposes RuntimeSchedulingManager but doesn't orchestrate."""
    context = RuntimeContext()
    manager = context.runtime_scheduling_manager
    assert isinstance(manager, RuntimeSchedulingManager)
    
    # Context should not have methods to evaluate schedule
    assert not hasattr(context, 'evaluate_schedule')
    assert not hasattr(context, 'record_schedule')


def test_dependency_direction():
    """
    Verify that RuntimeSchedulingManager depends on RuntimeRetryManager, 
    but RuntimeRetryManager doesn't depend on RuntimeSchedulingManager.
    """
    from runtime.core.runtime_retry_manager import RuntimeRetryManager
    
    manager_file = Path(inspect.getfile(RuntimeSchedulingManager))
    retry_file = Path(inspect.getfile(RuntimeRetryManager))
    
    # SchedulingManager SHOULD import RuntimeRetryManager
    assert "RuntimeRetryManager" in manager_file.read_text()
    
    # RuntimeRetryManager SHOULD NOT import RuntimeSchedulingManager
    assert "RuntimeSchedulingManager" not in retry_file.read_text()
