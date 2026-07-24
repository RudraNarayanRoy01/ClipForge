from dataclasses import FrozenInstanceError
import pytest

from src.runtime.core.context import RuntimeContext
from src.runtime.core.planner import (
    PlanningRequest,
    ExecutionPlan,
    PlanningStatus,
    RuntimeExecutionPlanner
)
from src.runtime.core.scheduler import (
    SchedulerResult,
    SchedulingStatus
)
from src.runtime.core.providers import ProviderIdentity

class TestRuntimeExecutionPlanner:
    """
    Lightweight architectural tests for the Runtime Execution Planner.
    
    These tests validate architectural boundaries, immutability, 
    and the "One Component -> One Primary Artifact" ownership model.
    """

    def test_planning_request_immutability(self):
        """PlanningRequest must be completely immutable after creation."""
        scheduler_result = SchedulerResult(
            status=SchedulingStatus.SCHEDULED,
            execution_placement=None,
            execution_ordering="IMMEDIATE",
            scheduling_reasoning="Test"
        )
        
        request = PlanningRequest(
            scheduler_result=scheduler_result,
            execution_intent="TEST_INTENT",
            workload_identity="test-123",
            planning_constraints={},
            planning_metadata={}
        )
        
        with pytest.raises(FrozenInstanceError):
            request.execution_intent = "MODIFIED"

    def test_execution_plan_immutability(self):
        """ExecutionPlan must be completely immutable after creation."""
        plan = ExecutionPlan(
            status=PlanningStatus.PLANNED,
            logical_execution_stages=["Stage 1"],
            planning_rationale="Test",
            planning_metadata={}
        )
        
        with pytest.raises(FrozenInstanceError):
            plan.status = PlanningStatus.INVALID_REQUEST

    def test_runtime_context_integration(self):
        """RuntimeContext must expose the RuntimeExecutionPlanner as the canonical subsystem."""
        context = RuntimeContext()
        planner = context.execution_planner
        
        assert planner is not None
        assert isinstance(planner, RuntimeExecutionPlanner)

    def test_planner_consumes_scheduler_result_and_produces_execution_plan(self):
        """
        RuntimeExecutionPlanner must consume a SchedulerResult (via PlanningRequest)
        and produce a valid ExecutionPlan containing only logical execution stages.
        """
        planner = RuntimeExecutionPlanner()
        
        scheduler_result = SchedulerResult(
            status=SchedulingStatus.SCHEDULED,
            execution_placement=ProviderIdentity("test_provider"),
            execution_ordering="IMMEDIATE",
            scheduling_reasoning="Test placement"
        )
        
        request = PlanningRequest(
            scheduler_result=scheduler_result,
            execution_intent="VIDEO_PROCESSING",
            workload_identity="workload-456"
        )
        
        plan = planner.plan(request)
        
        assert isinstance(plan, ExecutionPlan)
        assert plan.status == PlanningStatus.PLANNED
        assert len(plan.logical_execution_stages) > 0
        assert "Speech Recognition" in plan.logical_execution_stages
        
        # Verify no graph topology or execution nodes exist in the artifact
        assert not hasattr(plan, "nodes")
        assert not hasattr(plan, "edges")
        assert not hasattr(plan, "topology")
        assert not hasattr(plan, "parallel_execution")

    def test_planner_invalid_request(self):
        """RuntimeExecutionPlanner should handle invalid requests architecturally."""
        planner = RuntimeExecutionPlanner()
        
        request = PlanningRequest(
            scheduler_result=None,  # type: ignore # intentional for test
            execution_intent="TEST",
            workload_identity="test"
        )
        
        plan = planner.plan(request)
        
        assert plan.status == PlanningStatus.INVALID_REQUEST
        assert len(plan.logical_execution_stages) == 0
