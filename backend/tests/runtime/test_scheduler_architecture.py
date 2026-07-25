import pytest
import inspect
from dataclasses import is_dataclass
from typing import Any

from src.runtime.core.scheduler import RuntimeScheduler
from src.runtime.core.scheduling_model import (
    SchedulingIdentity,
    SchedulingDecision,
    SchedulingStatus,
    SchedulingPriority,
    SchedulingPolicy,
    SchedulingStrategy,
    QueueClassification
)
from src.runtime.core.execution_model import ExecutionRequest, ExecutionIdentity


class TestSchedulerArchitecture:
    """
    Structural verification of the Runtime Scheduler and its Domain Model.
    Ensures strict adherence to the architectural invariants.
    """

    def test_scheduling_artifacts_are_immutable(self) -> None:
        """
        Verify that scheduling decision artifacts are strictly immutable value objects.
        """
        assert is_dataclass(SchedulingIdentity)
        assert SchedulingIdentity.__dataclass_params__.frozen is True

        assert is_dataclass(SchedulingDecision)
        assert SchedulingDecision.__dataclass_params__.frozen is True

    def test_scheduler_has_no_execution_behavior(self) -> None:
        """
        Verify that RuntimeScheduler does NOT contain methods for execution.
        """
        methods = [name for name, _ in inspect.getmembers(RuntimeScheduler, predicate=inspect.isfunction)]
        
        forbidden_methods = [
            "execute", 
            "run", 
            "retry", 
            "start", 
            "stop",
            "allocate",
            "monitor",
            "process",
            "poll"
        ]
        
        for forbidden in forbidden_methods:
            assert forbidden not in methods, f"RuntimeScheduler must not contain forbidden method: {forbidden}"

    def test_scheduler_is_policy_neutral(self) -> None:
        """
        Verify that the Scheduler evaluates policy rather than defining it.
        We ensure it accepts policy parameters instead of hardcoding them internally.
        """
        scheduler = RuntimeScheduler()
        
        # Ensure 'schedule' method signature requires these to be provided or defaulted via kwargs
        sig = inspect.signature(scheduler.schedule)
        assert "policy" in sig.parameters
        assert "strategy" in sig.parameters
        assert "priority" in sig.parameters
        assert "queue_classification" in sig.parameters

    def test_scheduling_decision_ownership(self) -> None:
        """
        Verify that RuntimeScheduler produces SchedulingDecision.
        """
        scheduler = RuntimeScheduler()
        sig = inspect.signature(scheduler.schedule)
        
        assert sig.return_annotation is SchedulingDecision, "Scheduler must return SchedulingDecision"
        
        # Create dummy request
        identity = ExecutionIdentity(execution_id="test_1", created_at=100.0)
        request = ExecutionRequest(identity=identity)
        
        decision = scheduler.schedule(
            request=request,
            policy=SchedulingPolicy.IMMEDIATE,
            strategy=SchedulingStrategy.FIFO,
            priority=SchedulingPriority.HIGH,
            queue_classification=QueueClassification.BATCH
        )
        
        assert isinstance(decision, SchedulingDecision)
        assert decision.execution_identity.execution_id == "test_1"
        assert decision.policy == SchedulingPolicy.IMMEDIATE
        assert decision.strategy == SchedulingStrategy.FIFO
        assert decision.priority == SchedulingPriority.HIGH
        assert decision.queue_classification == QueueClassification.BATCH

    def test_queue_classification_is_declarative(self) -> None:
        """
        Verify QueueClassification contains no implementation logic.
        It should only be an Enum.
        """
        assert issubclass(QueueClassification, str)

    def test_scheduling_status_is_declarative(self) -> None:
        """
        Verify SchedulingStatus contains no implementation logic.
        """
        assert issubclass(SchedulingStatus, str)

    def test_scheduling_priority_is_declarative(self) -> None:
        """
        Verify SchedulingPriority contains no implementation logic.
        """
        assert issubclass(SchedulingPriority, str)

    def test_scheduling_policy_is_declarative(self) -> None:
        """
        Verify SchedulingPolicy contains no implementation logic.
        """
        assert issubclass(SchedulingPolicy, str)
        
    def test_scheduling_strategy_is_declarative(self) -> None:
        """
        Verify SchedulingStrategy contains no implementation logic.
        """
        assert issubclass(SchedulingStrategy, str)
