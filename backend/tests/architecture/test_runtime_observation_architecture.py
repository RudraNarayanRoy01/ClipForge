import pytest
import inspect
from enum import Enum
from dataclasses import is_dataclass
from src.runtime.domain.runtime_observation_model import (
    RuntimeObservationState,
    RuntimeObservationType,
    RuntimeObservationReason,
    RuntimeSignal,
    RuntimeSnapshot,
    RuntimeObservationInfo,
    RuntimeObservationResult
)


class TestRuntimeObservationArchitecture:
    """
    Architecture Certification Tests for Runtime Observation Domain.
    Ensures strict adherence to passive domain rules and prevents forbidden dependencies.
    """

    def test_runtime_observation_state_is_passive_enum(self):
        assert issubclass(RuntimeObservationState, Enum)
        # Ensure no behavioral methods
        methods = [m for m in dir(RuntimeObservationState) if callable(getattr(RuntimeObservationState, m)) and not m.startswith('_')]
        assert len(methods) == 0, f"RuntimeObservationState must not have behavioral methods. Found: {methods}"

    def test_runtime_observation_type_is_passive_enum(self):
        assert issubclass(RuntimeObservationType, Enum)
        methods = [m for m in dir(RuntimeObservationType) if callable(getattr(RuntimeObservationType, m)) and not m.startswith('_')]
        assert len(methods) == 0, f"RuntimeObservationType must not have behavioral methods. Found: {methods}"

    def test_runtime_signal_is_passive_enum(self):
        assert issubclass(RuntimeSignal, Enum)
        methods = [m for m in dir(RuntimeSignal) if callable(getattr(RuntimeSignal, m)) and not m.startswith('_')]
        assert len(methods) == 0, f"RuntimeSignal must not have behavioral methods. Found: {methods}"

    def test_runtime_observation_reason_is_immutable(self):
        assert is_dataclass(RuntimeObservationReason)
        assert RuntimeObservationReason.__dataclass_params__.frozen == True
        methods = [m for m in dir(RuntimeObservationReason) if callable(getattr(RuntimeObservationReason, m)) and not m.startswith('_')]
        assert len(methods) == 0, f"RuntimeObservationReason must not have behavioral methods. Found: {methods}"

    def test_runtime_snapshot_is_immutable_and_restricted(self):
        assert is_dataclass(RuntimeSnapshot)
        assert RuntimeSnapshot.__dataclass_params__.frozen == True
        methods = [m for m in dir(RuntimeSnapshot) if callable(getattr(RuntimeSnapshot, m)) and not m.startswith('_')]
        assert len(methods) == 0, f"RuntimeSnapshot must not have behavioral methods. Found: {methods}"

        fields = RuntimeSnapshot.__dataclass_fields__
        # Must only contain basic snapshot fields
        allowed_fields = {'snapshot_id', 'provider_id', 'observation_type', 'observation_state', 'captured_at'}
        assert set(fields.keys()) == allowed_fields

        # Check for forbidden terms in fields
        forbidden = ['metrics', 'health', 'retry', 'schedule', 'confidence', 'recommendation', 'reasoning', 'gpu', 'cpu', 'latency', 'duration']
        for field_name in fields.keys():
            for f in forbidden:
                assert f not in field_name.lower(), f"Forbidden field '{field_name}' in RuntimeSnapshot"

    def test_runtime_observation_info_is_immutable_and_restricted(self):
        assert is_dataclass(RuntimeObservationInfo)
        assert RuntimeObservationInfo.__dataclass_params__.frozen == True
        methods = [m for m in dir(RuntimeObservationInfo) if callable(getattr(RuntimeObservationInfo, m)) and not m.startswith('_')]
        assert len(methods) == 0, f"RuntimeObservationInfo must not have behavioral methods. Found: {methods}"

        fields = RuntimeObservationInfo.__dataclass_fields__
        allowed_fields = {'observation_id', 'snapshot_id', 'provider_id', 'signal', 'observation_state', 'created_at', 'updated_at'}
        assert set(fields.keys()) == allowed_fields

    def test_runtime_observation_result_is_immutable_transport(self):
        assert is_dataclass(RuntimeObservationResult)
        assert RuntimeObservationResult.__dataclass_params__.frozen == True
        methods = [m for m in dir(RuntimeObservationResult) if callable(getattr(RuntimeObservationResult, m)) and not m.startswith('_')]
        assert len(methods) == 0, f"RuntimeObservationResult must not have behavioral methods. Found: {methods}"

        fields = RuntimeObservationResult.__dataclass_fields__
        allowed_fields = {'observation_info', 'observation_summary', 'validation_result', 'timestamp'}
        assert set(fields.keys()) == allowed_fields
        
    def test_no_forbidden_dependencies(self):
        import src.runtime.domain.runtime_observation_model as model
        source = inspect.getsource(model)
        forbidden_imports = [
            'asyncio',
            'threading',
            'multiprocessing',
            'requests',
            'http',
            'RuntimeDecisionEngine',
            'RuntimeObservationManager',
            'RuntimeExecutionManager'
        ]
        for imp in forbidden_imports:
            assert imp not in source, f"Forbidden import '{imp}' found in runtime_observation_model.py"
