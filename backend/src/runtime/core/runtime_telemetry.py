from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, List

from .runtime_monitoring import MonitoringResult


class TelemetryStatus(Enum):
    """
    Lifecycle status of a Runtime telemetry capture.
    
    This represents telemetry capture lifecycle ONLY.
    It MUST NEVER contain execution state, monitoring state, metrics, health,
    diagnostics, optimization recommendations, or learning persistence.
    """
    CAPTURED = auto()
    PARTIAL = auto()
    FAILED = auto()
    INVALID = auto()


@dataclass(frozen=True)
class StageTelemetrySnapshot:
    """
    Immutable telemetry artifact for one execution stage.
    
    Represents captured Runtime signals for a single stage.
    It MUST NEVER contain:
    - metrics
    - health evaluations
    - diagnostics
    - optimization recommendations
    - learning knowledge
    - benchmarking
    - provider implementation details
    """
    stage_identifier: str
    stage_name: str
    status: TelemetryStatus
    signals: Dict[str, Any] = field(default_factory=dict)
    capture_timestamp: float = 0.0


@dataclass(frozen=True)
class TelemetrySnapshot:
    """
    Immutable Runtime canonical Telemetry artifact.
    
    Represents captured Runtime signals for one completed monitoring session.
    It MUST NEVER contain:
    - metrics
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
    stage_telemetry_snapshots: List[StageTelemetrySnapshot] = field(default_factory=list)
    status: TelemetryStatus = TelemetryStatus.INVALID
    signals: Dict[str, Any] = field(default_factory=dict)
    capture_metadata: Dict[str, Any] = field(default_factory=dict)
    capture_timestamp: float = 0.0


class RuntimeTelemetry:
    """
    The canonical Runtime signal capture layer.
    
    Responsibilities:
    - Consume immutable MonitoringResult
    - Capture Runtime signals
    - Produce immutable TelemetrySnapshot
    - Produce immutable StageTelemetrySnapshot
    - Preserve Runtime architectural boundaries
    - Remain deterministic
    - Remain provider independent
    - Remain hardware independent
    
    Must NEVER:
    - Execute work
    - Modify MonitoringResult
    - Modify AdaptationDecision
    - Modify ExecutionResult
    - Perform provider selection
    - Perform scheduling
    - Perform planning
    - Allocate resources
    - Modify execution context
    - Modify orchestration
    - Retry execution
    - Adapt execution
    - Optimize execution
    - Compute Runtime metrics
    - Infer Runtime health
    - Perform diagnostics
    - Benchmark Runtime performance
    - Persist learning
    - Store historical Runtime intelligence
    """

    def __init__(self) -> None:
        pass

    def capture_signals(self, monitoring_result: MonitoringResult, current_time: float) -> TelemetrySnapshot:
        """
        Consume immutable MonitoringResult and produce immutable TelemetrySnapshot.
        Preserves architectural boundaries by strictly decoupling signal capture from monitoring.
        """
        if not monitoring_result or monitoring_result.session_id == "invalid":
            return TelemetrySnapshot(
                session_id="invalid",
                status=TelemetryStatus.INVALID,
                capture_metadata={"error": "No valid monitoring result provided."},
                capture_timestamp=current_time
            )

        stage_snapshots: List[StageTelemetrySnapshot] = []
        
        for stage_observation in monitoring_result.stage_monitoring_results:
            # Create a snapshot representing signals captured for the stage
            snapshot = StageTelemetrySnapshot(
                stage_identifier=stage_observation.stage_identifier,
                stage_name=stage_observation.stage_name,
                status=TelemetryStatus.CAPTURED,
                signals={"source": "deterministic_telemetry_capture"},
                capture_timestamp=current_time
            )
            stage_snapshots.append(snapshot)

        return TelemetrySnapshot(
            session_id=monitoring_result.session_id,
            stage_telemetry_snapshots=stage_snapshots,
            status=TelemetryStatus.CAPTURED,
            signals={"session_signals_captured": True},
            capture_metadata={"captured_by": "RuntimeTelemetry"},
            capture_timestamp=current_time
        )
