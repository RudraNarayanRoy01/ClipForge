import pytest
from unittest.mock import Mock, call

from src.runtime.core.intent import ExecutionIntent
from src.runtime.core.planning_context import PlanningContext
from src.runtime.core.execution_planner import ExecutionPlanner
from src.runtime.core.planning_result import PlanningResult
from src.runtime.core.policy_engine import PolicyEngine
from src.runtime.core.policy_decision import PolicyDecision
from src.runtime.core.routing_engine import RoutingEngine
from src.runtime.core.route_decision import RouteDecision
from src.runtime.core.target_selector import TargetSelector
from src.runtime.core.execution_target import ExecutionTarget, TargetDescription
from src.runtime.composition.runtime_pipeline_context import RuntimePipelineContext
from src.runtime.invocation.runtime_pipeline import RuntimePipeline


@pytest.fixture
def mock_planner():
    return Mock(spec=ExecutionPlanner)


@pytest.fixture
def mock_policy():
    return Mock(spec=PolicyEngine)


@pytest.fixture
def mock_router():
    return Mock(spec=RoutingEngine)


@pytest.fixture
def mock_selector():
    return Mock(spec=TargetSelector)


@pytest.fixture
def pipeline_context(mock_planner, mock_policy, mock_router, mock_selector):
    return RuntimePipelineContext(
        execution_planner=mock_planner,
        policy_engine=mock_policy,
        routing_engine=mock_router,
        target_selector=mock_selector
    )


@pytest.fixture
def pipeline(pipeline_context):
    return RuntimePipeline(pipeline_context)


def test_construction(pipeline_context, mock_planner, mock_policy, mock_router, mock_selector):
    # A. Construction
    p = RuntimePipeline(pipeline_context)
    # Ensure it retains the context
    assert p._context is pipeline_context
    # Ensure it does not construct its own instances
    assert p._context.execution_planner is mock_planner
    assert p._context.policy_engine is mock_policy
    assert p._context.routing_engine is mock_router
    assert p._context.target_selector is mock_selector


def test_happy_path_and_propagation(pipeline, mock_planner, mock_policy, mock_router, mock_selector):
    # B. Happy path
    # C, D, E, F, G: Exact artifact propagation
    intent = ExecutionIntent(capability_id="test", payload={"opaque": True})
    context = PlanningContext()
    targets = [TargetDescription(target_id="t1", target_class="local", provider="p1")]

    # Set up unique mock return values to test identity propagation
    planning_result = Mock(spec=PlanningResult)
    policy_decision = Mock(spec=PolicyDecision)
    route_decision = Mock(spec=RouteDecision)
    execution_target = Mock(spec=ExecutionTarget)

    mock_planner.plan.return_value = planning_result
    mock_policy.evaluate.return_value = policy_decision
    mock_router.evaluate.return_value = route_decision
    mock_selector.select.return_value = execution_target

    result = pipeline.process(intent, context, targets)

    # D & E: Intent and context propagation to planner
    mock_planner.plan.assert_called_once()
    assert mock_planner.plan.call_args.kwargs['intent'] is intent
    assert mock_planner.plan.call_args.kwargs['context'] is context

    # C & E: exact artifact propagation to policy
    mock_policy.evaluate.assert_called_once()
    assert mock_policy.evaluate.call_args.kwargs['planning_result'] is planning_result
    assert mock_policy.evaluate.call_args.kwargs['context'] is context

    # C: exact artifact propagation to router
    mock_router.evaluate.assert_called_once()
    assert mock_router.evaluate.call_args.kwargs['policy_decision'] is policy_decision

    # C & F: exact artifact propagation to selector
    mock_selector.select.assert_called_once()
    assert mock_selector.select.call_args.kwargs['route_decision'] is route_decision
    assert mock_selector.select.call_args.kwargs['available_targets'] is targets

    # G: Result propagation
    assert result is execution_target


def test_policy_rejection(pipeline, mock_planner, mock_policy, mock_router, mock_selector):
    # H. Policy rejection
    intent = ExecutionIntent(capability_id="test", payload="opaque")
    context = PlanningContext()
    targets = []

    planning_result = Mock(spec=PlanningResult)
    # Certified contract states that if policy rejects, routing yields is_routed=False and selector yields None
    policy_decision = Mock(spec=PolicyDecision, is_approved=False)
    route_decision = Mock(spec=RouteDecision, is_routed=False)

    mock_planner.plan.return_value = planning_result
    mock_policy.evaluate.return_value = policy_decision
    mock_router.evaluate.return_value = route_decision
    mock_selector.select.return_value = None

    result = pipeline.process(intent, context, targets)

    mock_selector.select.assert_called_once()
    assert mock_selector.select.call_args.kwargs['route_decision'] is route_decision
    assert mock_selector.select.call_args.kwargs['available_targets'] is targets
    assert result is None


def test_routing_failure(pipeline, mock_planner, mock_policy, mock_router, mock_selector):
    # I. Routing failure
    intent = ExecutionIntent(capability_id="test", payload="opaque")
    context = PlanningContext()
    targets = []

    planning_result = Mock(spec=PlanningResult)
    policy_decision = Mock(spec=PolicyDecision, is_approved=True)
    # Unroutable decision
    route_decision = Mock(spec=RouteDecision, is_routed=False)

    mock_planner.plan.return_value = planning_result
    mock_policy.evaluate.return_value = policy_decision
    mock_router.evaluate.return_value = route_decision
    mock_selector.select.return_value = None

    result = pipeline.process(intent, context, targets)

    mock_selector.select.assert_called_once()
    assert mock_selector.select.call_args.kwargs['route_decision'] is route_decision
    assert mock_selector.select.call_args.kwargs['available_targets'] is targets
    assert result is None


def test_target_absence_and_no_fallback(pipeline, mock_planner, mock_policy, mock_router, mock_selector):
    # J & K. Target absence and no arbitrary fallback
    intent = ExecutionIntent(capability_id="test", payload="opaque")
    context = PlanningContext()
    targets = []

    planning_result = Mock(spec=PlanningResult)
    policy_decision = Mock(spec=PolicyDecision, is_approved=True)
    route_decision = Mock(spec=RouteDecision, is_routed=True)

    mock_planner.plan.return_value = planning_result
    mock_policy.evaluate.return_value = policy_decision
    mock_router.evaluate.return_value = route_decision
    # Certified selector returns None when no target matches
    mock_selector.select.return_value = None

    result = pipeline.process(intent, context, targets)

    # Pipeline does not synthesize a target, just returns what selector returned
    assert result is None
    # Selector was only called once, no loops/fallback attempts by the pipeline itself
    assert mock_selector.select.call_count == 1


def test_payload_opacity_and_immutability(pipeline, mock_planner, mock_policy, mock_router, mock_selector):
    # L & M. Payload opacity & Immutability
    original_payload = {"sensitive": "data", "id": 123}
    intent = ExecutionIntent(capability_id="test", payload=original_payload)
    context = PlanningContext(quality_preference="high")
    targets = (TargetDescription(target_id="t1", target_class="local", provider="p1"),)

    planning_result = Mock(spec=PlanningResult)
    policy_decision = Mock(spec=PolicyDecision)
    route_decision = Mock(spec=RouteDecision)
    execution_target = Mock(spec=ExecutionTarget)

    mock_planner.plan.return_value = planning_result
    mock_policy.evaluate.return_value = policy_decision
    mock_router.evaluate.return_value = route_decision
    mock_selector.select.return_value = execution_target

    result = pipeline.process(intent, context, targets)

    # Ensure intent payload hasn't been modified
    assert intent.payload == {"sensitive": "data", "id": 123}
    assert context.quality_preference == "high"
    assert len(targets) == 1

    # Exact instance propagation ensures pipeline doesn't rebuild or mutate input identity
    mock_planner.plan.assert_called_once()
    assert mock_planner.plan.call_args.kwargs['intent'] is intent
    assert mock_planner.plan.call_args.kwargs['context'] is context


def test_determinism(pipeline, mock_planner, mock_policy, mock_router, mock_selector):
    # N. Determinism
    intent = ExecutionIntent(capability_id="test", payload="opaque")
    context = PlanningContext()
    targets = []

    planning_result = Mock(spec=PlanningResult)
    policy_decision = Mock(spec=PolicyDecision)
    route_decision = Mock(spec=RouteDecision)
    execution_target = Mock(spec=ExecutionTarget)

    mock_planner.plan.return_value = planning_result
    mock_policy.evaluate.return_value = policy_decision
    mock_router.evaluate.return_value = route_decision
    mock_selector.select.return_value = execution_target

    result1 = pipeline.process(intent, context, targets)
    result2 = pipeline.process(intent, context, targets)

    assert result1 is execution_target
    assert result2 is execution_target
    assert mock_planner.plan.call_count == 2
    assert mock_policy.evaluate.call_count == 2
    assert mock_router.evaluate.call_count == 2
    assert mock_selector.select.call_count == 2
