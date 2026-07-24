from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, List

from .runtime_health import RuntimeHealthReport, RuntimeHealthStatus


class RuntimeDiagnosticStatus(Enum):
    """
    Lifecycle status of Runtime diagnostic reasoning.
    
    This represents diagnostic classification ONLY.
    It MUST NEVER contain:
    - Optimization
    - Recommendations
    - Policy decisions
    - Learning
    """
    NORMAL = auto()
    INFORMATIONAL = auto()
    INVESTIGATING = auto()
    WARNING = auto()
    CRITICAL = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class StageRuntimeDiagnostic:
    """
    Immutable Runtime diagnostic artifact for one execution stage.
    
    Represents the diagnostic reasoning for one execution stage.
    It MUST NEVER contain:
    - Optimization hints
    - Execution actions
    - Recommendations
    - Policy information
    - Learning
    - Benchmarking
    """
    stage_identifier: str
    stage_name: str
    status: RuntimeDiagnosticStatus
    finding: str = "No finding"
    probable_cause: str = "Unknown"
    confidence_level: float = 0.0
    diagnostic_timestamp: float = 0.0
    diagnostic_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeDiagnosticsReport:
    """
    Immutable Runtime canonical Diagnostics Report artifact.
    
    Represents the diagnostic interpretation of one completed Runtime health evaluation.
    It MUST NEVER contain:
    - Optimization recommendations
    - Adaptation recommendations
    - Scheduling recommendations
    - Provider recommendations
    - Execution decisions
    - Learned knowledge
    - Historical Runtime memory
    - Policy decisions
    - Benchmark information
    """
    session_id: str
    stage_diagnostics_collection: List[StageRuntimeDiagnostic] = field(default_factory=list)
    status: RuntimeDiagnosticStatus = RuntimeDiagnosticStatus.UNKNOWN
    findings: List[str] = field(default_factory=list)
    probable_causes: List[str] = field(default_factory=list)
    confidence_level: float = 0.0
    diagnostic_timestamp: float = 0.0
    diagnostic_metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimeDiagnostics:
    """
    The canonical Runtime diagnostic reasoning subsystem.
    
    Responsibilities:
    - Consume immutable RuntimeHealthReport
    - Analyze Runtime operational condition
    - Correlate Runtime health observations
    - Determine probable causes
    - Classify Runtime diagnostic findings
    - Produce immutable RuntimeDiagnosticsReport
    - Produce immutable StageRuntimeDiagnostic
    - Preserve Runtime architectural boundaries
    - Remain deterministic
    - Remain provider independent
    - Remain hardware independent
    
    Must NEVER:
    - Execute work
    - Modify RuntimeHealthReport or any other artifact
    - Optimize Runtime execution
    - Recommend corrective actions
    - Recommend adaptation
    - Recommend scheduling
    - Recommend provider selection
    - Modify Runtime behavior
    - Benchmark providers or hardware
    - Persist Runtime knowledge
    - Learn from historical executions
    """

    def __init__(self) -> None:
        pass

    def diagnose_health(self, health_report: RuntimeHealthReport, current_time: float) -> RuntimeDiagnosticsReport:
        """
        Consume immutable RuntimeHealthReport and produce immutable RuntimeDiagnosticsReport.
        Preserves architectural boundaries by strictly decoupling diagnostic reasoning from health evaluation.
        """
        if not health_report or health_report.session_id == "invalid":
            return RuntimeDiagnosticsReport(
                session_id="invalid",
                status=RuntimeDiagnosticStatus.UNKNOWN,
                findings=["Invalid health report"],
                probable_causes=["No valid health report provided"],
                diagnostic_metadata={"error": "No valid health report provided."},
                diagnostic_timestamp=current_time
            )

        stage_diagnostics_list: List[StageRuntimeDiagnostic] = []
        overall_status = RuntimeDiagnosticStatus.NORMAL
        overall_findings = []
        overall_probable_causes = []
        
        for stage_health in health_report.stage_health_collection:
            status = RuntimeDiagnosticStatus.NORMAL
            finding = "Operational parameters within expected boundaries."
            probable_cause = "Normal execution."
            
            if stage_health.status == RuntimeHealthStatus.DEGRADED:
                status = RuntimeDiagnosticStatus.WARNING
                finding = f"Stage {stage_health.stage_name} operational health degraded."
                probable_cause = "Potential resource contention or provider latency."
                overall_status = max(overall_status, RuntimeDiagnosticStatus.WARNING, key=lambda s: s.value)
            elif stage_health.status == RuntimeHealthStatus.WARNING:
                status = RuntimeDiagnosticStatus.WARNING
                finding = f"Stage {stage_health.stage_name} operational health warning."
                probable_cause = "Sub-optimal provider response or minor constraint."
                overall_status = max(overall_status, RuntimeDiagnosticStatus.WARNING, key=lambda s: s.value)
            elif stage_health.status == RuntimeHealthStatus.CRITICAL:
                status = RuntimeDiagnosticStatus.CRITICAL
                finding = f"Stage {stage_health.stage_name} operational health critical."
                probable_cause = "Provider failure or hardware resource exhaustion."
                overall_status = RuntimeDiagnosticStatus.CRITICAL
            elif stage_health.status == RuntimeHealthStatus.UNKNOWN:
                status = RuntimeDiagnosticStatus.INVESTIGATING
                finding = f"Stage {stage_health.stage_name} operational health unknown."
                probable_cause = "Missing or corrupted health evaluation data."
                overall_status = max(overall_status, RuntimeDiagnosticStatus.INVESTIGATING, key=lambda s: s.value)

            stage_diagnostic = StageRuntimeDiagnostic(
                stage_identifier=stage_health.stage_identifier,
                stage_name=stage_health.stage_name,
                status=status,
                finding=finding,
                probable_cause=probable_cause,
                confidence_level=0.9,
                diagnostic_timestamp=current_time,
                diagnostic_metadata={"evaluated_health_status": stage_health.status.name}
            )
            stage_diagnostics_list.append(stage_diagnostic)
            
            if status != RuntimeDiagnosticStatus.NORMAL:
                overall_findings.append(finding)
                overall_probable_causes.append(probable_cause)

        if not overall_findings:
            overall_findings.append("All stages operating normally.")
            overall_probable_causes.append("Standard operational conditions.")

        # Determine overall status based on report status if stage list was empty
        if not stage_diagnostics_list:
            if health_report.status == RuntimeHealthStatus.CRITICAL:
                overall_status = RuntimeDiagnosticStatus.CRITICAL
            elif health_report.status in (RuntimeHealthStatus.DEGRADED, RuntimeHealthStatus.WARNING):
                overall_status = RuntimeDiagnosticStatus.WARNING

        return RuntimeDiagnosticsReport(
            session_id=health_report.session_id,
            stage_diagnostics_collection=stage_diagnostics_list,
            status=overall_status,
            findings=overall_findings,
            probable_causes=overall_probable_causes,
            confidence_level=0.85,
            diagnostic_timestamp=current_time,
            diagnostic_metadata={"diagnosed_by": "RuntimeDiagnostics", "stages_diagnosed": len(stage_diagnostics_list)}
        )
