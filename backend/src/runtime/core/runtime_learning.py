from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, List

from .runtime_optimization import OptimizationDecision, StageOptimizationDecision, OptimizationPriority


class KnowledgeClassification(Enum):
    """
    Immutable classification representing the maturity of learned Runtime knowledge.
    
    NEVER execution priority.
    NEVER scheduler priority.
    NEVER optimization priority.
    """
    STABLE = auto()
    EMERGING = auto()
    EXPERIMENTAL = auto()
    TRANSIENT = auto()
    DEPRECATED = auto()


@dataclass(frozen=True)
class StageRuntimeKnowledge:
    """
    Immutable learned Runtime knowledge for one execution stage.
    
    Represents knowledge consolidation only.
    It MUST NEVER contain:
    - Execution
    - Scheduling
    - Resource allocation
    - Adaptation
    - Active optimization
    - Runtime mutations
    - Policy
    """
    stage_identifier: str
    stage_name: str
    knowledge_classification: KnowledgeClassification
    learned_pattern: str = "No pattern identified"
    learning_rationale: str = "No learning rationale"
    knowledge_confidence: float = 0.0
    knowledge_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeKnowledge:
    """
    Immutable canonical Runtime Knowledge artifact.
    
    Represents reusable Runtime knowledge derived from one completed optimization evaluation.
    It MUST NEVER contain:
    - Executed actions
    - Runtime mutations
    - Scheduling decisions
    - Resource allocations
    - Provider selections
    - Adaptation results
    - Active optimization decisions
    - Learned execution policies
    - Benchmark information
    """
    session_id: str
    stage_knowledge_collection: List[StageRuntimeKnowledge] = field(default_factory=list)
    knowledge_classifications: List[str] = field(default_factory=list)
    learned_patterns: List[str] = field(default_factory=list)
    learning_confidence: float = 0.0
    knowledge_timestamp: float = 0.0
    knowledge_metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimeLearning:
    """
    The canonical Runtime Learning knowledge persistence subsystem.
    
    Responsibilities:
    - Consume immutable OptimizationDecision
    - Analyze completed optimization decisions
    - Consolidate reusable Runtime knowledge
    - Identify stable optimization patterns
    - Classify learned Runtime knowledge
    - Produce immutable RuntimeKnowledge
    - Produce immutable StageRuntimeKnowledge
    - Preserve Runtime architectural boundaries
    - Remain deterministic
    - Remain provider independent
    - Remain hardware independent
    
    Must NEVER:
    - Execute work
    - Modify OptimizationDecision or any other artifact
    - Perform optimization
    - Perform provider selection
    - Perform scheduling
    - Perform planning
    - Allocate resources
    - Modify execution context
    - Retry execution
    - Adapt execution
    - Execute learning
    - Execute Runtime mutations
    - Benchmark providers
    - Benchmark hardware
    """

    def __init__(self) -> None:
        pass

    def learn(self, optimization_decision: OptimizationDecision, current_time: float) -> RuntimeKnowledge:
        """
        Consume immutable OptimizationDecision and produce immutable RuntimeKnowledge.
        Preserves architectural boundaries by strictly decoupling knowledge persistence from active optimization.
        """
        if not optimization_decision or optimization_decision.session_id == "invalid":
            return RuntimeKnowledge(
                session_id="invalid",
                knowledge_classifications=["Invalid optimization decision"],
                learned_patterns=["No knowledge extracted"],
                knowledge_metadata={"error": "No valid optimization decision provided."},
                knowledge_timestamp=current_time
            )

        stage_knowledges: List[StageRuntimeKnowledge] = []
        overall_classifications = []
        overall_patterns = []
        
        for stage_optimization in optimization_decision.stage_optimization_collection:
            classification = KnowledgeClassification.TRANSIENT
            pattern = "Observed Standard Behavior"
            rationale = "Insufficient optimization data for long-term learning."
            
            # Map optimization priority/classification to learning concepts without executing or adopting policy
            if stage_optimization.priority == OptimizationPriority.CRITICAL:
                classification = KnowledgeClassification.STABLE
                pattern = f"Critical Failure Pattern: {stage_optimization.optimization_classification}"
                rationale = f"Consolidated knowledge from high-priority optimization: {stage_optimization.optimization_intent}"
            elif stage_optimization.priority == OptimizationPriority.MEDIUM:
                classification = KnowledgeClassification.EMERGING
                pattern = f"Performance Variance Pattern: {stage_optimization.optimization_classification}"
                rationale = f"Observed recurring optimization intent: {stage_optimization.optimization_intent}"
            elif stage_optimization.priority == OptimizationPriority.LOW:
                classification = KnowledgeClassification.EXPERIMENTAL
                pattern = f"Telemetry Fluctuation: {stage_optimization.optimization_classification}"
                rationale = "Recording minor optimizations for future baseline comparison."
            
            stage_knowledge = StageRuntimeKnowledge(
                stage_identifier=stage_optimization.stage_identifier,
                stage_name=stage_optimization.stage_name,
                knowledge_classification=classification,
                learned_pattern=pattern,
                learning_rationale=rationale,
                knowledge_confidence=stage_optimization.confidence_level * 0.9, # Derived confidence
                knowledge_metadata={"source_optimization_priority": stage_optimization.priority.name}
            )
            stage_knowledges.append(stage_knowledge)
            
            if classification != KnowledgeClassification.TRANSIENT:
                overall_classifications.append(classification.name)
                overall_patterns.append(pattern)

        if not overall_classifications:
            overall_classifications.append("Baseline Operation")
            overall_patterns.append("Stable execution without required optimizations")

        return RuntimeKnowledge(
            session_id=optimization_decision.session_id,
            stage_knowledge_collection=stage_knowledges,
            knowledge_classifications=overall_classifications,
            learned_patterns=overall_patterns,
            learning_confidence=optimization_decision.decision_confidence * 0.9, # Derived confidence
            knowledge_timestamp=current_time,
            knowledge_metadata={"learned_by": "RuntimeLearning", "stages_learned": len(stage_knowledges)}
        )
