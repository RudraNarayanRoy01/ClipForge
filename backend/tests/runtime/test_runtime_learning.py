from dataclasses import FrozenInstanceError
import pytest
import time

from src.runtime.core.runtime_optimization import OptimizationDecision, StageOptimizationDecision, OptimizationPriority
from src.runtime.core.runtime_learning import RuntimeLearning, RuntimeKnowledge, StageRuntimeKnowledge, KnowledgeClassification
from src.runtime.core.context import RuntimeContext


def test_runtime_knowledge_immutability():
    """Validate that RuntimeKnowledge is immutable."""
    knowledge = RuntimeKnowledge(
        session_id="test_session",
        stage_knowledge_collection=[],
        knowledge_classifications=["Baseline Operation"],
        learned_patterns=["Stable execution"],
        learning_confidence=0.9,
        knowledge_timestamp=time.time(),
        knowledge_metadata={}
    )
    
    with pytest.raises(FrozenInstanceError):
        knowledge.session_id = "new_session"

    with pytest.raises(FrozenInstanceError):
        knowledge.learning_confidence = 0.99


def test_stage_runtime_knowledge_immutability():
    """Validate that StageRuntimeKnowledge is immutable."""
    stage_knowledge = StageRuntimeKnowledge(
        stage_identifier="test_stage",
        stage_name="Test Stage",
        knowledge_classification=KnowledgeClassification.STABLE,
        learned_pattern="Test Pattern",
        learning_rationale="Test Rationale",
        knowledge_confidence=0.8,
        knowledge_metadata={}
    )
    
    with pytest.raises(FrozenInstanceError):
        stage_knowledge.stage_identifier = "new_stage"


def test_runtime_context_exposes_runtime_learning():
    """Validate that RuntimeContext exposes RuntimeLearning."""
    context = RuntimeContext()
    assert hasattr(context, "runtime_learning")
    assert isinstance(context.runtime_learning, RuntimeLearning)


def test_runtime_learning_consumes_optimization_decision():
    """Validate RuntimeLearning consumes OptimizationDecision and produces RuntimeKnowledge."""
    learning = RuntimeLearning()
    
    stage_opt = StageOptimizationDecision(
        stage_identifier="stage_1",
        stage_name="Data Ingestion",
        priority=OptimizationPriority.CRITICAL,
        optimization_classification="Memory Optimization",
        optimization_intent="Reduce batch size",
        optimization_rationale="OOM risk detected",
        confidence_level=0.95,
        optimization_metadata={}
    )
    
    decision = OptimizationDecision(
        session_id="session_123",
        stage_optimization_collection=[stage_opt],
        priority=OptimizationPriority.CRITICAL,
        optimization_classifications=["Memory Optimization"],
        optimization_intents=["Reduce batch size"],
        decision_confidence=0.9,
        optimization_timestamp=time.time(),
        optimization_metadata={}
    )
    
    current_time = time.time()
    knowledge = learning.learn(decision, current_time)
    
    assert isinstance(knowledge, RuntimeKnowledge)
    assert knowledge.session_id == "session_123"
    assert len(knowledge.stage_knowledge_collection) == 1
    
    stage_knowledge = knowledge.stage_knowledge_collection[0]
    assert stage_knowledge.stage_identifier == "stage_1"
    assert stage_knowledge.knowledge_classification == KnowledgeClassification.STABLE
    
    # Ensure optimization decision was not modified
    assert decision.priority == OptimizationPriority.CRITICAL
    assert len(decision.stage_optimization_collection) == 1


def test_runtime_learning_invalid_input():
    """Validate RuntimeLearning handles invalid inputs gracefully."""
    learning = RuntimeLearning()
    
    invalid_decision = OptimizationDecision(
        session_id="invalid",
        stage_optimization_collection=[]
    )
    
    current_time = time.time()
    knowledge = learning.learn(invalid_decision, current_time)
    
    assert knowledge.session_id == "invalid"
    assert "Invalid optimization decision" in knowledge.knowledge_classifications


def test_knowledge_classification_lifecycle():
    """Validate the KnowledgeClassification Enum has the required lifecycle values."""
    classifications = [c.name for c in KnowledgeClassification]
    assert "STABLE" in classifications
    assert "EMERGING" in classifications
    assert "EXPERIMENTAL" in classifications
    assert "TRANSIENT" in classifications
    assert "DEPRECATED" in classifications
