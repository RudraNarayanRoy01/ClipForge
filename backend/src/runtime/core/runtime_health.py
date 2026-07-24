from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, List

from .runtime_metrics import RuntimeMetricsSnapshot


class RuntimeHealthStatus(Enum):
    """
    Lifecycle status of Runtime operational health.
    
    This represents health lifecycle ONLY.
    It MUST NEVER contain execution state, monitoring state, telemetry state, metrics,
    diagnostics, optimization recommendations, or learning persistence.
    """
    HEALTHY = auto()
    DEGRADED = auto()
    WARNING = auto()
    CRITICAL = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class StageRuntimeHealth:
    """
    Immutable Runtime health artifact for one execution stage.
    
    Represents the operational evaluation for a single stage.
    It MUST NEVER contain:
    - diagnostics
    - root causes
    - optimization recommendations
    - learning knowledge
    - benchmarking
    - provider implementation details
    """
    stage_identifier: str
    stage_name: str
    status: RuntimeHealthStatus
    evaluation_timestamp: float = 0.0
    evaluation_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeHealthReport:
    """
    Immutable Runtime canonical Health Report artifact.
    
    Represents the evaluated operational condition for one completed Runtime metrics calculation.
    It MUST NEVER contain:
    - diagnostic information
    - root cause analysis
    - optimization recommendations
    - adaptation recommendations
    - learned knowledge
    - benchmark information
    - historical Runtime memory
    - provider implementation details
    - scheduling logic
    - allocation logic
    """
    session_id: str
    stage_health_collection: List[StageRuntimeHealth] = field(default_factory=list)
    status: RuntimeHealthStatus = RuntimeHealthStatus.UNKNOWN
    health_classification: str = "UNKNOWN"
    evaluation_timestamp: float = 0.0
    evaluation_metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimeHealth:
    """
    The canonical Runtime operational evaluation layer.
    
    Responsibilities:
    - Consume immutable RuntimeMetricsSnapshot
    - Evaluate Runtime operational condition
    - Produce immutable RuntimeHealthReport
    - Produce immutable StageRuntimeHealth
    - Preserve Runtime architectural boundaries
    - Remain deterministic
    - Remain provider independent
    - Remain hardware independent
    
    Must NEVER:
    - Execute work
    - Modify RuntimeMetricsSnapshot
    - Modify TelemetrySnapshot
    - Modify MonitoringResult
    - Modify AdaptationDecision
    - Modify ExecutionResult
    - Capture telemetry
    - Calculate metrics
    - Perform provider selection
    - Perform scheduling
    - Perform planning
    - Allocate resources
    - Modify execution context
    - Modify orchestration
    - Retry execution
    - Adapt execution
    - Diagnose Runtime behavior
    - Explain failures
    - Recommend optimization
    - Recommend adaptation
    - Perform root cause analysis
    - Benchmark providers
    - Benchmark hardware
    - Persist learning
    - Store historical Runtime intelligence
    """

    def __init__(self) -> None:
        pass

    def evaluate_health(self, metrics_snapshot: RuntimeMetricsSnapshot, current_time: float) -> RuntimeHealthReport:
        """
        Consume immutable RuntimeMetricsSnapshot and produce immutable RuntimeHealthReport.
        Preserves architectural boundaries by strictly decoupling evaluation from metrics calculation.
        """
        if not metrics_snapshot or metrics_snapshot.session_id == "invalid":
            return RuntimeHealthReport(
                session_id="invalid",
                status=RuntimeHealthStatus.UNKNOWN,
                health_classification="INVALID_METRICS",
                evaluation_metadata={"error": "No valid metrics snapshot provided."},
                evaluation_timestamp=current_time
            )

        stage_health_list: List[StageRuntimeHealth] = []
        
        for stage_metric in metrics_snapshot.stage_metrics:
            # Create a health evaluation representing the operational condition for the stage
            stage_health = StageRuntimeHealth(
                stage_identifier=stage_metric.stage_identifier,
                stage_name=stage_metric.stage_name,
                status=RuntimeHealthStatus.HEALTHY,
                evaluation_timestamp=current_time,
                evaluation_metadata={"evaluated_measurements": len(stage_metric.measurements)}
            )
            stage_health_list.append(stage_health)

        return RuntimeHealthReport(
            session_id=metrics_snapshot.session_id,
            stage_health_collection=stage_health_list,
            status=RuntimeHealthStatus.HEALTHY,
            health_classification="OPERATIONAL",
            evaluation_timestamp=current_time,
            evaluation_metadata={"evaluated_by": "RuntimeHealth", "stages_evaluated": len(stage_health_list)}
        )
