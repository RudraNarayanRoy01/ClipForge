from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, List

from .adaptive_runtime import AdaptationDecision, StageAdaptationDecision


class MonitoringStatus(Enum):
    """
    Lifecycle status of a Runtime observation.
    
    This represents monitoring lifecycle ONLY.
    It MUST NEVER contain execution state, adaptation state, or optimization metrics.
    """
    OBSERVED = auto()
    PARTIAL = auto()
    FAILED = auto()
    INVALID = auto()


@dataclass(frozen=True)
class StageMonitoringResult:
    """
    Immutable observation artifact for one execution stage.
    
    Represents purely what was observed for a single stage.
    It MUST NEVER contain:
    - adaptation decisions
    - optimization information
    - telemetry streams
    - runtime metrics
    - diagnostics
    - learning history
    - provider implementation details
    """
    stage_identifier: str
    stage_name: str
    status: MonitoringStatus
    observation_summary: str = ""
    observation_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MonitoringResult:
    """
    Immutable Runtime canonical Monitoring artifact.
    
    Represents observations for one completed execution session.
    It MUST NEVER contain:
    - adaptation recommendations
    - optimization recommendations
    - telemetry streams
    - runtime metrics
    - diagnostics
    - benchmark information
    - learned knowledge
    - historical Runtime memory
    - provider implementation details
    - scheduling logic
    - allocation logic
    """
    session_id: str
    stage_monitoring_results: List[StageMonitoringResult] = field(default_factory=list)
    status: MonitoringStatus = MonitoringStatus.INVALID
    observation_summary: str = ""
    observation_metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimeMonitoring:
    """
    The canonical Runtime observation layer.
    
    Responsibilities:
    - Consume immutable AdaptationDecision
    - Observe completed Runtime execution and adaptation
    - Produce immutable MonitoringResult
    - Produce immutable StageMonitoringResult
    - Preserve Runtime architectural boundaries
    - Remain deterministic
    - Remain provider independent
    - Remain hardware independent
    
    Must NEVER:
    - Execute work
    - Modify ExecutionResult
    - Modify AdaptationDecision
    - Perform provider selection
    - Perform scheduling
    - Perform planning
    - Allocate resources
    - Modify execution context
    - Modify orchestration
    - Retry execution
    - Adapt execution
    - Optimize execution
    - Collect telemetry streams
    - Generate runtime metrics
    - Perform diagnostics
    - Persist learning
    - Store historical intelligence
    """

    def __init__(self) -> None:
        pass

    def observe_adaptation(self, adaptation_decision: AdaptationDecision) -> MonitoringResult:
        """
        Consume immutable AdaptationDecision and produce immutable MonitoringResult.
        Preserves architectural boundaries by strictly decoupling observation from adaptation.
        """
        if not adaptation_decision or adaptation_decision.session_id == "invalid":
            return MonitoringResult(
                session_id="invalid",
                status=MonitoringStatus.INVALID,
                observation_summary="No valid adaptation decision provided."
            )

        stage_observations: List[StageMonitoringResult] = []
        
        for stage_decision in adaptation_decision.stage_decisions:
            # Create an observation solely based on the presence of the adaptation decision
            observation = StageMonitoringResult(
                stage_identifier=stage_decision.stage_identifier,
                stage_name=stage_decision.stage_name,
                status=MonitoringStatus.OBSERVED,
                observation_summary=f"Observed adaptation decision for stage {stage_decision.stage_name}",
                observation_metadata={"source": "deterministic_monitoring_observation"}
            )
            stage_observations.append(observation)

        return MonitoringResult(
            session_id=adaptation_decision.session_id,
            stage_monitoring_results=stage_observations,
            status=MonitoringStatus.OBSERVED,
            observation_summary="Observation completed for session.",
            observation_metadata={"observed_by": "RuntimeMonitoring"}
        )
