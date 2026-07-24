import pytest
import time
from dataclasses import FrozenInstanceError

from src.runtime.core.runtime_learning import RuntimeKnowledge, StageRuntimeKnowledge, KnowledgeClassification
from src.runtime.core.runtime_planning import RuntimePlanning, PlanningDecision


def test_planning_decision_immutability():
    """Verify PlanningDecision immutability."""
    decision = PlanningDecision(
        session_id="test-session",
        planning_objective="Test Objective",
        planning_rationale="Test Rationale",
        planning_confidence=0.9
    )
    
    with pytest.raises(FrozenInstanceError):
        decision.planning_objective = "New Objective"  # type: ignore
        
    with pytest.raises(FrozenInstanceError):
        decision.planning_confidence = 1.0  # type: ignore


def test_runtime_planning_ownership_and_direction():
    """Verify RuntimePlanning consumes RuntimeKnowledge and produces PlanningDecision."""
    planning = RuntimePlanning()
    
    knowledge = RuntimeKnowledge(
        session_id="test-session",
        stage_knowledge_collection=[
            StageRuntimeKnowledge(
                stage_identifier="stage-1",
                stage_name="Test Stage",
                knowledge_classification=KnowledgeClassification.STABLE,
                learned_pattern="Test Pattern",
                learning_rationale="Test Rationale",
                knowledge_confidence=0.8
            )
        ],
        knowledge_classifications=["STABLE"],
        learned_patterns=["Test Pattern"],
        learning_confidence=0.8,
        knowledge_timestamp=time.time()
    )
    
    decision = planning.plan(knowledge, time.time())
    
    # Verify outputs
    assert isinstance(decision, PlanningDecision)
    assert decision.session_id == "test-session"
    assert decision.planning_objective is not None
    assert decision.planning_rationale is not None
    
    # Verify no execution, routing, or provider concepts exist
    assert not hasattr(decision, "execute")
    assert not hasattr(decision, "provider")
    assert not hasattr(decision, "gpu")
    assert not hasattr(decision, "schedule")


def test_provider_and_hardware_independence():
    """Verify PlanningDecision does not reference specific providers or hardware."""
    decision = PlanningDecision(
        session_id="test-session",
        planning_objective="General optimization",
        planning_rationale="Baseline metrics",
    )
    
    # Converting to string to ensure no accidental inclusion in fields
    decision_str = str(decision).lower()
    
    forbidden_terms = [
        "gemini", "openai", "claude", "ollama", "llama", "mistral",
        "cpu", "gpu", "cuda", "rocm", "metal", "vram"
    ]
    
    for term in forbidden_terms:
        assert term not in decision_str, f"Found forbidden term '{term}' in PlanningDecision"


def test_invalid_knowledge_handling():
    """Verify RuntimePlanning handles invalid RuntimeKnowledge gracefully."""
    planning = RuntimePlanning()
    
    invalid_knowledge = RuntimeKnowledge(
        session_id="invalid",
        knowledge_timestamp=time.time()
    )
    
    decision = planning.plan(invalid_knowledge, time.time())
    
    assert decision.session_id == "invalid"
    assert "Invalid" in decision.planning_assumptions[0]


def test_planning_decision_purity():
    """Verify PlanningDecision purity by ensuring it contains only planning information."""
    decision = PlanningDecision(
        session_id="test-session",
        planning_objective="Purity test",
        planning_rationale="Verifying artifact purity"
    )
    
    # Allowed attributes
    allowed_attributes = {
        "session_id", "planning_objective", "planning_rationale",
        "planning_confidence", "planning_assumptions", "planning_metadata"
    }
    
    # Check that there are no additional attributes (purity)
    actual_attributes = {k for k in decision.__dict__.keys() if not k.startswith('_')}
    assert actual_attributes.issubset(allowed_attributes), f"Found unexpected attributes: {actual_attributes - allowed_attributes}"

    # Explicitly verify rejection of specific forbidden domains
    forbidden_domains = [
        "schedule", "scheduling_data", "provider_selection", "routing_decision",
        "routing", "hardware_decision", "execution_command", "policy_evaluation",
        "resource_allocation"
    ]
    for domain in forbidden_domains:
        assert not hasattr(decision, domain)


def test_runtime_context_ownership():
    """Verify RuntimeContext owns RuntimePlanning and dependency direction is maintained."""
    from src.runtime.core.context import RuntimeContext
    
    context = RuntimeContext()
    
    # Verify RuntimeContext is the composition root for Planning
    assert hasattr(context, "runtime_planning")
    assert isinstance(context.runtime_planning, RuntimePlanning)
    
    # Verify RuntimePlanning does not instantiate secondary composition roots
    planning = context.runtime_planning
    
    forbidden_dependencies = [
        "runtime_learning", "runtime_optimization", "runtime_monitoring",
        "runtime_telemetry", "runtime_metrics", "runtime_health",
        "runtime_diagnostics"
    ]
    
    for dep in forbidden_dependencies:
        assert not hasattr(planning, dep), f"RuntimePlanning must not construct {dep}"
