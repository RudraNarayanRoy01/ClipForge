from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, List

from .runtime_telemetry import TelemetrySnapshot


class RuntimeMetricStatus(Enum):
    """
    Lifecycle status of a metric calculation.
    
    This represents metric calculation lifecycle ONLY.
    It MUST NEVER contain execution state, monitoring state, telemetry state, health,
    diagnostics, optimization recommendations, or learning persistence.
    """
    CALCULATED = auto()
    PARTIAL = auto()
    FAILED = auto()
    INVALID = auto()


@dataclass(frozen=True)
class StageRuntimeMetrics:
    """
    Immutable Runtime metric artifact for one execution stage.
    
    Represents quantitative measurements for a single stage.
    It MUST NEVER contain:
    - health evaluations
    - diagnostics
    - optimization recommendations
    - learning knowledge
    - benchmarking
    - provider implementation details
    """
    stage_identifier: str
    stage_name: str
    status: RuntimeMetricStatus
    measurements: Dict[str, float] = field(default_factory=dict)
    calculation_timestamp: float = 0.0


@dataclass(frozen=True)
class RuntimeMetricsSnapshot:
    """
    Immutable Runtime canonical Metrics artifact.
    
    Represents quantitative measurements for one completed telemetry capture.
    It MUST NEVER contain:
    - health evaluations
    - diagnostic information
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
    stage_metrics: List[StageRuntimeMetrics] = field(default_factory=list)
    status: RuntimeMetricStatus = RuntimeMetricStatus.INVALID
    measurements: Dict[str, float] = field(default_factory=dict)
    calculation_metadata: Dict[str, Any] = field(default_factory=dict)
    calculation_timestamp: float = 0.0


class RuntimeMetrics:
    """
    The canonical Runtime quantitative measurement layer.
    
    Responsibilities:
    - Consume immutable TelemetrySnapshot
    - Derive quantitative Runtime measurements
    - Produce immutable RuntimeMetricsSnapshot
    - Produce immutable StageRuntimeMetrics
    - Preserve Runtime architectural boundaries
    - Remain deterministic
    - Remain provider independent
    - Remain hardware independent
    
    Must NEVER:
    - Execute work
    - Modify TelemetrySnapshot
    - Modify MonitoringResult
    - Modify AdaptationDecision
    - Modify ExecutionResult
    - Capture telemetry
    - Perform provider selection
    - Perform scheduling
    - Perform planning
    - Allocate resources
    - Modify execution context
    - Modify orchestration
    - Retry execution
    - Adapt execution
    - Evaluate Runtime health
    - Diagnose Runtime behavior
    - Recommend optimization
    - Recommend adaptation
    - Benchmark hardware
    - Persist learning
    - Store historical Runtime intelligence
    """

    def __init__(self) -> None:
        pass

    def calculate_metrics(self, telemetry_snapshot: TelemetrySnapshot, current_time: float) -> RuntimeMetricsSnapshot:
        """
        Consume immutable TelemetrySnapshot and produce immutable RuntimeMetricsSnapshot.
        Preserves architectural boundaries by strictly decoupling metric calculation from telemetry capture.
        """
        if not telemetry_snapshot or telemetry_snapshot.session_id == "invalid":
            return RuntimeMetricsSnapshot(
                session_id="invalid",
                status=RuntimeMetricStatus.INVALID,
                calculation_metadata={"error": "No valid telemetry snapshot provided."},
                calculation_timestamp=current_time
            )

        stage_metrics_list: List[StageRuntimeMetrics] = []
        
        for stage_telemetry in telemetry_snapshot.stage_telemetry_snapshots:
            # Create a snapshot representing metrics calculated for the stage
            stage_metric = StageRuntimeMetrics(
                stage_identifier=stage_telemetry.stage_identifier,
                stage_name=stage_telemetry.stage_name,
                status=RuntimeMetricStatus.CALCULATED,
                measurements={"processed_signals_count": float(len(stage_telemetry.signals))},
                calculation_timestamp=current_time
            )
            stage_metrics_list.append(stage_metric)

        return RuntimeMetricsSnapshot(
            session_id=telemetry_snapshot.session_id,
            stage_metrics=stage_metrics_list,
            status=RuntimeMetricStatus.CALCULATED,
            measurements={"total_stages_measured": float(len(stage_metrics_list))},
            calculation_metadata={"calculated_by": "RuntimeMetrics"},
            calculation_timestamp=current_time
        )
