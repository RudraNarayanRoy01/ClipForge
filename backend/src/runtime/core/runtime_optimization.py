from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, List

from .runtime_diagnostics import RuntimeDiagnosticsReport, RuntimeDiagnosticStatus


class OptimizationPriority(Enum):
    """
    Immutable priority representing optimization urgency only.
    
    NEVER execution priority.
    NEVER scheduler priority.
    NEVER resource priority.
    """
    NONE = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


@dataclass(frozen=True)
class StageOptimizationDecision:
    """
    Immutable optimization reasoning artifact for one execution stage.
    
    Represents optimization reasoning only.
    It MUST NEVER contain:
    - Execution
    - Scheduling
    - Resource allocation
    - Adaptation
    - Learning
    - Runtime mutations
    - Policy
    """
    stage_identifier: str
    stage_name: str
    priority: OptimizationPriority
    optimization_classification: str = "Unclassified"
    optimization_intent: str = "No intent"
    optimization_rationale: str = "No rationale"
    confidence_level: float = 0.0
    optimization_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OptimizationDecision:
    """
    Immutable Runtime canonical Optimization Decision artifact.
    
    Represents the optimization strategy derived from one completed Runtime diagnostics evaluation.
    It MUST NEVER contain:
    - Executed actions
    - Runtime mutations
    - Scheduling decisions
    - Resource allocations
    - Provider selections
    - Adaptation results
    - Learned knowledge
    - Historical Runtime memory
    - Policy decisions
    - Benchmark information
    """
    session_id: str
    stage_optimization_collection: List[StageOptimizationDecision] = field(default_factory=list)
    priority: OptimizationPriority = OptimizationPriority.NONE
    optimization_classifications: List[str] = field(default_factory=list)
    optimization_intents: List[str] = field(default_factory=list)
    decision_confidence: float = 0.0
    optimization_timestamp: float = 0.0
    optimization_metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimeOptimization:
    """
    The canonical Runtime optimization reasoning subsystem.
    
    Responsibilities:
    - Consume immutable RuntimeDiagnosticsReport
    - Analyze diagnostic findings
    - Determine optimization opportunities
    - Prioritize optimization decisions
    - Classify optimization intent
    - Produce immutable OptimizationDecision
    - Produce immutable StageOptimizationDecision
    - Preserve Runtime architectural boundaries
    - Remain deterministic
    - Remain provider independent
    - Remain hardware independent
    
    Must NEVER:
    - Execute work
    - Modify RuntimeDiagnosticsReport or any other artifact
    - Capture telemetry
    - Calculate metrics
    - Evaluate Runtime health
    - Diagnose Runtime
    - Perform provider selection
    - Perform scheduling
    - Perform planning
    - Allocate resources
    - Modify execution context
    - Retry execution
    - Adapt execution
    - Execute optimization
    - Persist learning
    - Store historical Runtime intelligence
    - Benchmark providers
    - Benchmark hardware
    """

    def __init__(self) -> None:
        pass

    def optimize(self, diagnostics_report: RuntimeDiagnosticsReport, current_time: float) -> OptimizationDecision:
        """
        Consume immutable RuntimeDiagnosticsReport and produce immutable OptimizationDecision.
        Preserves architectural boundaries by strictly decoupling optimization reasoning from execution.
        """
        if not diagnostics_report or diagnostics_report.session_id == "invalid":
            return OptimizationDecision(
                session_id="invalid",
                priority=OptimizationPriority.NONE,
                optimization_classifications=["Invalid diagnostic report"],
                optimization_intents=["No optimization possible"],
                optimization_metadata={"error": "No valid diagnostics report provided."},
                optimization_timestamp=current_time
            )

        stage_optimizations: List[StageOptimizationDecision] = []
        overall_priority = OptimizationPriority.NONE
        overall_classifications = []
        overall_intents = []
        
        for stage_diagnostic in diagnostics_report.stage_diagnostics_collection:
            priority = OptimizationPriority.NONE
            classification = "Standard Operation"
            intent = "Maintain current execution strategy"
            rationale = "No diagnostics findings requiring optimization."
            
            if stage_diagnostic.status == RuntimeDiagnosticStatus.WARNING:
                priority = OptimizationPriority.MEDIUM
                classification = "Performance Optimization"
                intent = "Investigate resource reallocation or provider tuning"
                rationale = f"Diagnostic warning found: {stage_diagnostic.finding}"
                overall_priority = max(overall_priority, OptimizationPriority.MEDIUM, key=lambda p: p.value)
            elif stage_diagnostic.status == RuntimeDiagnosticStatus.CRITICAL:
                priority = OptimizationPriority.CRITICAL
                classification = "Stability Optimization"
                intent = "Prioritize provider failover or load shedding"
                rationale = f"Critical diagnostic finding: {stage_diagnostic.finding}"
                overall_priority = OptimizationPriority.CRITICAL
            elif stage_diagnostic.status == RuntimeDiagnosticStatus.INVESTIGATING:
                priority = OptimizationPriority.LOW
                classification = "Telemetry Optimization"
                intent = "Increase monitoring fidelity"
                rationale = "Diagnostic information is insufficient."
                overall_priority = max(overall_priority, OptimizationPriority.LOW, key=lambda p: p.value)

            stage_optimization = StageOptimizationDecision(
                stage_identifier=stage_diagnostic.stage_identifier,
                stage_name=stage_diagnostic.stage_name,
                priority=priority,
                optimization_classification=classification,
                optimization_intent=intent,
                optimization_rationale=rationale,
                confidence_level=0.85,
                optimization_metadata={"source_diagnostic_status": stage_diagnostic.status.name}
            )
            stage_optimizations.append(stage_optimization)
            
            if priority != OptimizationPriority.NONE:
                overall_classifications.append(classification)
                overall_intents.append(intent)

        if not overall_classifications:
            overall_classifications.append("No optimizations needed")
            overall_intents.append("Maintain operation")

        # Determine overall priority based on report status if stage list was empty
        if not stage_optimizations:
            if diagnostics_report.status == RuntimeDiagnosticStatus.CRITICAL:
                overall_priority = OptimizationPriority.CRITICAL
            elif diagnostics_report.status == RuntimeDiagnosticStatus.WARNING:
                overall_priority = OptimizationPriority.MEDIUM

        return OptimizationDecision(
            session_id=diagnostics_report.session_id,
            stage_optimization_collection=stage_optimizations,
            priority=overall_priority,
            optimization_classifications=overall_classifications,
            optimization_intents=overall_intents,
            decision_confidence=0.8,
            optimization_timestamp=current_time,
            optimization_metadata={"optimized_by": "RuntimeOptimization", "stages_optimized": len(stage_optimizations)}
        )
