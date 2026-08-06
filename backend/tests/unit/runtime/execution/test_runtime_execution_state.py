import pytest
from src.runtime.execution import RuntimeExecutionState, ExecutionStage

def test_state_creation():
    state = RuntimeExecutionState(stage=ExecutionStage.VALIDATED)
    assert state.stage == ExecutionStage.VALIDATED

def test_state_immutability():
    state = RuntimeExecutionState(stage=ExecutionStage.READY)
    with pytest.raises(Exception):
        state.stage = ExecutionStage.UNINITIALIZED
