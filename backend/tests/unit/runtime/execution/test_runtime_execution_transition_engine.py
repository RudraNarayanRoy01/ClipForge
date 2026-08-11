import pytest
from unittest.mock import Mock, call

from src.runtime.domain.runtime_execution_model import RuntimeExecutionStatus
from src.runtime.execution.runtime_execution_outcome import RuntimeExecutionOutcome
from src.runtime.execution.runtime_execution_transition_engine import RuntimeExecutionTransitionEngine
from src.runtime.execution.runtime_execution_transition_validator import RuntimeExecutionTransitionValidator
from src.runtime.core.scheduling_model import SchedulingStatus


@pytest.fixture
def engine():
    return RuntimeExecutionTransitionEngine()


class TestRuntimeExecutionTransitionEngine:

    def test_valid_transitions(self, engine):
        """Test A: Valid transition tests"""
        valid_transitions = [
            (RuntimeExecutionStatus.PREPARED, RuntimeExecutionStatus.READY),
            (RuntimeExecutionStatus.READY, RuntimeExecutionStatus.EXECUTING),
            (RuntimeExecutionStatus.EXECUTING, RuntimeExecutionStatus.COMPLETED),
            (RuntimeExecutionStatus.EXECUTING, RuntimeExecutionStatus.FAILED),
        ]
        
        for current_status, target_status in valid_transitions:
            result = engine.transition(current_status, target_status)
            assert result is target_status

    def test_invalid_skipped_transitions(self, engine):
        """Test B: Invalid skipped transitions"""
        invalid_skipped = [
            (RuntimeExecutionStatus.PREPARED, RuntimeExecutionStatus.EXECUTING),
            (RuntimeExecutionStatus.PREPARED, RuntimeExecutionStatus.COMPLETED),
            (RuntimeExecutionStatus.PREPARED, RuntimeExecutionStatus.FAILED),
            (RuntimeExecutionStatus.READY, RuntimeExecutionStatus.COMPLETED),
            (RuntimeExecutionStatus.READY, RuntimeExecutionStatus.FAILED),
        ]
        
        for current_status, target_status in invalid_skipped:
            with pytest.raises(ValueError, match="Invalid Runtime Execution transition"):
                engine.transition(current_status, target_status)

    def test_invalid_regressions(self, engine):
        """Test C: Invalid regressions"""
        invalid_regressions = [
            (RuntimeExecutionStatus.EXECUTING, RuntimeExecutionStatus.READY),
            (RuntimeExecutionStatus.EXECUTING, RuntimeExecutionStatus.PREPARED),
            (RuntimeExecutionStatus.COMPLETED, RuntimeExecutionStatus.READY),
            (RuntimeExecutionStatus.COMPLETED, RuntimeExecutionStatus.EXECUTING),
            (RuntimeExecutionStatus.COMPLETED, RuntimeExecutionStatus.PREPARED),
            (RuntimeExecutionStatus.FAILED, RuntimeExecutionStatus.READY),
            (RuntimeExecutionStatus.FAILED, RuntimeExecutionStatus.EXECUTING),
            (RuntimeExecutionStatus.FAILED, RuntimeExecutionStatus.PREPARED),
            (RuntimeExecutionStatus.READY, RuntimeExecutionStatus.PREPARED),
        ]
        
        for current_status, target_status in invalid_regressions:
            with pytest.raises(ValueError, match="Invalid Runtime Execution transition"):
                engine.transition(current_status, target_status)

    def test_self_transitions(self, engine):
        """Test D: Self-transitions"""
        for status in RuntimeExecutionStatus:
            with pytest.raises(ValueError, match="Invalid Runtime Execution transition"):
                engine.transition(status, status)

    def test_aborted_isolation(self, engine):
        """Test E: ABORTED isolation"""
        # Incoming to ABORTED
        for status in RuntimeExecutionStatus:
            with pytest.raises(ValueError, match="Invalid Runtime Execution transition"):
                engine.transition(status, RuntimeExecutionStatus.ABORTED)
                
        # Outgoing from ABORTED
        for status in RuntimeExecutionStatus:
            # We already covered ABORTED -> ABORTED in self_transitions, but re-testing here is fine
            with pytest.raises(ValueError, match="Invalid Runtime Execution transition"):
                engine.transition(RuntimeExecutionStatus.ABORTED, status)

    def test_invalid_input_types(self, engine):
        """Test F: Invalid input types"""
        invalid_inputs = [
            None,
            "PREPARED",
            1,
            RuntimeExecutionOutcome.SUCCESS,
            RuntimeExecutionOutcome.FAILED,
            RuntimeExecutionOutcome.CANCELLED,
            SchedulingStatus.READY,
            SchedulingStatus.QUEUED,
            object(),
        ]
        
        # Test current_status invalid
        for invalid_input in invalid_inputs:
            with pytest.raises(ValueError, match="Invalid Runtime Execution transition"):
                engine.transition(invalid_input, RuntimeExecutionStatus.READY)
                
        # Test target_status invalid
        for invalid_input in invalid_inputs:
            with pytest.raises(ValueError, match="Invalid Runtime Execution transition"):
                engine.transition(RuntimeExecutionStatus.PREPARED, invalid_input)

    def test_validator_delegation(self):
        """Test G: Validator delegation"""
        mock_validator = Mock(spec=RuntimeExecutionTransitionValidator)
        # We define a custom rule: PREPARED -> READY is valid, others invalid according to mock
        mock_validator.is_valid.side_effect = lambda c, t: c == RuntimeExecutionStatus.PREPARED and t == RuntimeExecutionStatus.READY
        
        custom_engine = RuntimeExecutionTransitionEngine(validator=mock_validator)
        
        # Valid per mock
        result = custom_engine.transition(RuntimeExecutionStatus.PREPARED, RuntimeExecutionStatus.READY)
        assert result is RuntimeExecutionStatus.READY
        mock_validator.is_valid.assert_called_with(RuntimeExecutionStatus.PREPARED, RuntimeExecutionStatus.READY)
        
        # Invalid per mock
        with pytest.raises(ValueError, match="Invalid Runtime Execution transition"):
            custom_engine.transition(RuntimeExecutionStatus.READY, RuntimeExecutionStatus.EXECUTING)
        mock_validator.is_valid.assert_called_with(RuntimeExecutionStatus.READY, RuntimeExecutionStatus.EXECUTING)

    def test_statelessness(self, engine):
        """Test H: Statelessness"""
        # Sequential valid transitions shouldn't affect each other or retain state
        result1 = engine.transition(RuntimeExecutionStatus.PREPARED, RuntimeExecutionStatus.READY)
        assert result1 is RuntimeExecutionStatus.READY
        
        result2 = engine.transition(RuntimeExecutionStatus.READY, RuntimeExecutionStatus.EXECUTING)
        assert result2 is RuntimeExecutionStatus.EXECUTING
        
        # A later invalid transition shouldn't affect future valid ones
        with pytest.raises(ValueError):
            engine.transition(RuntimeExecutionStatus.PREPARED, RuntimeExecutionStatus.EXECUTING)
            
        result3 = engine.transition(RuntimeExecutionStatus.EXECUTING, RuntimeExecutionStatus.COMPLETED)
        assert result3 is RuntimeExecutionStatus.COMPLETED

    def test_result_semantics(self, engine):
        """Test I: Result semantics"""
        result = engine.transition(RuntimeExecutionStatus.PREPARED, RuntimeExecutionStatus.READY)
        assert result is RuntimeExecutionStatus.READY
        assert isinstance(result, RuntimeExecutionStatus)
