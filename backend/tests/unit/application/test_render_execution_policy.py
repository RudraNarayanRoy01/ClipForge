import pytest
from dataclasses import FrozenInstanceError
from datetime import datetime

from src.domain.render_plan import RenderPlan
from src.application.execution_models import RenderExecutionRequest, ValidatedRenderPlan
from src.application.render_execution_policy import (
    RenderExecutionPolicy,
    RenderExecutionPolicyRule,
    PolicyViolation,
    PolicyViolationSeverity,
    RenderExecutionDecision,
    RenderExecutionPolicyResult
)

import uuid
from src.domain.render_plan import (
    RenderPlan, RenderMetadata, RenderResolution, FrameRate, AspectRatio,
    RenderLayer, LayerCategory
)

class MockRule(RenderExecutionPolicyRule):
    def __init__(self, name: str, violations: list[PolicyViolation]):
        self._name = name
        self._violations = violations
        self.evaluation_count = 0

    @property
    def name(self) -> str:
        return self._name

    def evaluate(self, request: RenderExecutionRequest) -> list[PolicyViolation]:
        self.evaluation_count += 1
        return self._violations


@pytest.fixture
def dummy_request() -> RenderExecutionRequest:
    plan = RenderPlan(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        metadata=RenderMetadata(
            resolution=RenderResolution(1920, 1080),
            frame_rate=FrameRate(30.0),
            duration_seconds=10.0,
            aspect_ratio=AspectRatio(16, 9)
        ),
        layers=[
            RenderLayer(id=uuid.uuid4(), category=LayerCategory.VIDEO, name="Main", z_index=0)
        ]
    )
    validated = ValidatedRenderPlan(plan=plan, validated_at=datetime.utcnow())
    return RenderExecutionRequest(validated_plan=validated, output_destination="/out.mp4")


def test_policy_models_are_immutable():
    """Ensure that the data models are frozen to prevent accidental mutation."""
    violation = PolicyViolation(code="V1", description="desc", severity=PolicyViolationSeverity.WARNING)
    with pytest.raises(FrozenInstanceError):
        violation.code = "V2"
        
    result = RenderExecutionPolicyResult.allow()
    with pytest.raises(FrozenInstanceError):
        result.decision = RenderExecutionDecision.DENY


def test_policy_allows_execution(dummy_request):
    """Test that a request is ALLOWED when no rules return any violations."""
    rule1 = MockRule("RuleA", [])
    rule2 = MockRule("RuleB", [])
    
    policy = RenderExecutionPolicy(rules=[rule1, rule2])
    result = policy.evaluate(dummy_request)
    
    assert result.decision == RenderExecutionDecision.ALLOW
    assert len(result.violations) == 0
    assert rule1.evaluation_count == 1
    assert rule2.evaluation_count == 1


def test_policy_denies_execution_on_blocker(dummy_request):
    """Test that a request is DENIED if at least one BLOCKER violation is returned."""
    blocker = PolicyViolation("QUOTA_EXCEEDED", "Quota exceeded", PolicyViolationSeverity.BLOCKER)
    rule1 = MockRule("RuleA", [blocker])
    rule2 = MockRule("RuleB", [])
    
    policy = RenderExecutionPolicy(rules=[rule1, rule2])
    result = policy.evaluate(dummy_request)
    
    assert result.decision == RenderExecutionDecision.DENY
    assert len(result.violations) == 1
    assert result.violations[0] == blocker


def test_policy_allows_with_warnings(dummy_request):
    """Test that ALLOW_WITH_WARNINGS is returned when WARNING violations exist but no BLOCKERs."""
    warning = PolicyViolation("LONG_RENDER", "Render might take long", PolicyViolationSeverity.WARNING)
    rule1 = MockRule("RuleA", [warning])
    rule2 = MockRule("RuleB", [])
    
    policy = RenderExecutionPolicy(rules=[rule1, rule2])
    result = policy.evaluate(dummy_request)
    
    assert result.decision == RenderExecutionDecision.ALLOW_WITH_WARNINGS
    assert len(result.violations) == 1
    assert result.violations[0] == warning


def test_policy_evaluates_all_rules_even_on_blocker_and_aggregates_results(dummy_request):
    """Ensure policy does not fail fast and collects all warnings and blockers."""
    blocker = PolicyViolation("NO_LICENSE", "No license", PolicyViolationSeverity.BLOCKER)
    warning = PolicyViolation("LOW_SPACE", "Low disk space", PolicyViolationSeverity.WARNING)
    
    rule1 = MockRule("RuleA", [warning])
    rule2 = MockRule("RuleB", [blocker])
    rule3 = MockRule("RuleC", [])
    
    policy = RenderExecutionPolicy(rules=[rule1, rule2, rule3])
    result = policy.evaluate(dummy_request)
    
    # Check decision
    assert result.decision == RenderExecutionDecision.DENY
    
    # All rules should have been evaluated
    assert rule1.evaluation_count == 1
    assert rule2.evaluation_count == 1
    assert rule3.evaluation_count == 1
    
    # All violations should be aggregated
    assert len(result.violations) == 2
    assert warning in result.violations
    assert blocker in result.violations


def test_policy_deterministic_evaluation_order(dummy_request):
    """Ensure rules are evaluated in alphabetical order by name, regardless of registration order."""
    eval_order = []
    
    class OrderTrackingRule(RenderExecutionPolicyRule):
        def __init__(self, name: str):
            self._name = name
            
        @property
        def name(self) -> str:
            return self._name
            
        def evaluate(self, request: RenderExecutionRequest) -> list[PolicyViolation]:
            eval_order.append(self._name)
            return []

    # Passed in random order
    rules = [
        OrderTrackingRule("RuleC"),
        OrderTrackingRule("RuleA"),
        OrderTrackingRule("RuleB")
    ]
    
    policy = RenderExecutionPolicy(rules=rules)
    policy.evaluate(dummy_request)
    
    assert eval_order == ["RuleA", "RuleB", "RuleC"]
