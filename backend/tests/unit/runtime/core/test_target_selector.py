import pytest
from dataclasses import FrozenInstanceError

from src.runtime.core.intent import ExecutionIntent
from src.runtime.core.planning_result import PlanningResult
from src.runtime.core.policy_decision import PolicyDecision
from src.runtime.core.route_decision import RouteDecision
from src.runtime.core.execution_target import ExecutionTarget, TargetDescription
from src.runtime.core.target_selector import TargetSelector


def create_dummy_route_decision(execution_class: str, is_routed: bool, fallback_allowed: bool) -> RouteDecision:
    intent = ExecutionIntent(capability_id="test_capability", payload={"opaque": "data"})
    planning_result = PlanningResult(
        intent=intent,
        strategy="test_strategy",
        requirements=("test_req",)
    )
    policy_decision = PolicyDecision(
        planning_result=planning_result,
        is_approved=True,
        policy_mode="test",
        fallback_allowed=fallback_allowed
    )
    return RouteDecision(
        policy_decision=policy_decision,
        execution_class=execution_class,
        is_routed=is_routed,
        fallback_allowed=fallback_allowed
    )


@pytest.fixture
def available_targets():
    return [
        TargetDescription(
            target_id="target_1",
            target_class="local",
            provider="ollama",
            model="gemma4:latest",
            compute_class="local_gpu"
        ),
        TargetDescription(
            target_id="target_2",
            target_class="remote",
            provider="openai",
            model="gpt-4o",
            compute_class="remote_compute"
        ),
        TargetDescription(
            target_id="target_3",
            target_class="balanced",
            provider="gemini",
            model="gemini-1.5-pro",
            compute_class="remote_compute"
        )
    ]


@pytest.fixture
def target_selector():
    return TargetSelector()


def test_valid_route_decision_produces_target(target_selector, available_targets):
    route = create_dummy_route_decision(execution_class="abstract_local", is_routed=True, fallback_allowed=False)
    
    target = target_selector.select(route, available_targets)
    
    assert target is not None
    assert isinstance(target, ExecutionTarget)
    assert target.target_id == "target_1"
    assert target.provider == "ollama"


def test_rejected_route_decision_produces_no_target(target_selector, available_targets):
    route = create_dummy_route_decision(execution_class="abstract_local", is_routed=False, fallback_allowed=False)
    
    target = target_selector.select(route, available_targets)
    
    assert target is None


def test_target_selection_is_deterministic(target_selector, available_targets):
    route = create_dummy_route_decision(execution_class="abstract_remote", is_routed=True, fallback_allowed=False)
    
    target1 = target_selector.select(route, available_targets)
    target2 = target_selector.select(route, available_targets)
    
    assert target1 == target2
    assert target1.target_id == "target_2"


def test_correct_abstract_class_matching(target_selector, available_targets):
    route_local = create_dummy_route_decision(execution_class="abstract_local", is_routed=True, fallback_allowed=False)
    route_remote = create_dummy_route_decision(execution_class="abstract_remote", is_routed=True, fallback_allowed=False)
    route_balanced = create_dummy_route_decision(execution_class="abstract_balanced", is_routed=True, fallback_allowed=False)
    
    assert target_selector.select(route_local, available_targets).target_class == "local"
    assert target_selector.select(route_remote, available_targets).target_class == "remote"
    assert target_selector.select(route_balanced, available_targets).target_class == "balanced"


def test_identity_preservation(target_selector, available_targets):
    route = create_dummy_route_decision(execution_class="abstract_local", is_routed=True, fallback_allowed=False)
    target = target_selector.select(route, available_targets)
    
    # Must preserve the exact same route decision object
    assert target.route_decision is route


def test_target_immutability(target_selector, available_targets):
    route = create_dummy_route_decision(execution_class="abstract_local", is_routed=True, fallback_allowed=False)
    target = target_selector.select(route, available_targets)
    
    with pytest.raises(FrozenInstanceError):
        target.target_id = "new_id"


def test_no_input_mutation(target_selector, available_targets):
    route = create_dummy_route_decision(execution_class="abstract_local", is_routed=True, fallback_allowed=False)
    original_routed_state = route.is_routed
    original_class = route.execution_class
    
    target_selector.select(route, available_targets)
    
    assert route.is_routed == original_routed_state
    assert route.execution_class == original_class


def test_payload_opacity(target_selector, available_targets):
    # The payload is entirely untouched, we just assert we don't need or check it
    route = create_dummy_route_decision(execution_class="abstract_local", is_routed=True, fallback_allowed=False)
    target = target_selector.select(route, available_targets)
    
    assert target is not None
    # We never accessed route.policy_decision.planning_result.intent.payload


def test_provider_identity_without_implementation(target_selector, available_targets):
    route = create_dummy_route_decision(execution_class="abstract_local", is_routed=True, fallback_allowed=False)
    target = target_selector.select(route, available_targets)
    
    assert isinstance(target.provider, str)
    assert target.provider == "ollama"
    assert not hasattr(target, "execute")
    assert not hasattr(target, "client")


def test_model_identity_without_execution(target_selector, available_targets):
    route = create_dummy_route_decision(execution_class="abstract_local", is_routed=True, fallback_allowed=False)
    target = target_selector.select(route, available_targets)
    
    assert isinstance(target.model, str)
    assert target.model == "gemma4:latest"
    assert not hasattr(target, "run")
    assert not hasattr(target, "invoke")


def test_compute_classification_descriptive(target_selector, available_targets):
    route = create_dummy_route_decision(execution_class="abstract_local", is_routed=True, fallback_allowed=False)
    target = target_selector.select(route, available_targets)
    
    assert isinstance(target.compute_class, str)
    assert target.compute_class == "local_gpu"
    assert not hasattr(target, "gpu_id")
    assert not hasattr(target, "allocate")


def test_no_execution_occurs(target_selector, available_targets):
    route = create_dummy_route_decision(execution_class="abstract_local", is_routed=True, fallback_allowed=False)
    target = target_selector.select(route, available_targets)
    
    assert not hasattr(target, "execute")
    assert not hasattr(target, "run")


def test_incompatible_fallback_must_not_occur(target_selector, available_targets):
    # Requesting an unknown class, but fallback is allowed
    # TargetSelector must NOT arbitrarily pick a target when there's no explicit compatible fallback.
    route = create_dummy_route_decision(execution_class="abstract_unknown_class", is_routed=True, fallback_allowed=True)
    target = target_selector.select(route, available_targets)
    
    assert target is None


def test_no_fallback_produces_none(target_selector, available_targets):
    # Requesting an unknown class, but fallback is NOT allowed
    route = create_dummy_route_decision(execution_class="abstract_unknown_class", is_routed=True, fallback_allowed=False)
    target = target_selector.select(route, available_targets)
    
    assert target is None


def test_multiple_compatible_targets(target_selector, available_targets):
    # Add a second local target
    available_targets.append(TargetDescription(
        target_id="target_4",
        target_class="local",
        provider="llama_cpp",
        model="llama3",
        compute_class="local_cpu"
    ))
    
    route = create_dummy_route_decision(execution_class="abstract_local", is_routed=True, fallback_allowed=False)
    target = target_selector.select(route, available_targets)
    
    # Must deterministically select the first one in the sequence ordering
    assert target is not None
    assert target.target_id == "target_1"
