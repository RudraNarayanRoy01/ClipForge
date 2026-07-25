from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any


class RuntimeConfidenceState(Enum):
    """
    Represents the immutable lifecycle of a Runtime Confidence artifact.
    Lifecycle categorization only. No behavior.
    """
    INITIALIZED = "INITIALIZED"
    EVALUATING = "EVALUATING"
    ASSESSED = "ASSESSED"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class RuntimeConfidenceLevel(Enum):
    """
    Represents structural confidence levels.
    Represents Runtime structural confidence ONLY (e.g. completeness, consistency, structural integrity, 
    availability of required evidence/upstream artifacts, internal coherence).
    NOT statistical probability. NOT AI confidence. NOT prediction confidence.
    NOT likelihood or inference certainty. It never evaluates correctness or truthfulness.
    """
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class RuntimeConfidenceFactor:
    """
    Represents immutable confidence metadata.
    Contains information describing why confidence was assigned.
    Metadata only. No scoring algorithm. No behavioral logic.
    """
    factor_id: str
    factor_type: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeConfidenceEvidence:
    """
    Represents immutable evidence references supporting the confidence artifact.
    Contains ONLY evidence identifiers, evidence references, evidence metadata, 
    and evidence classification.
    NEVER embeds RuntimeReasoning, RuntimeObservation, or RuntimeDecision artifacts.
    NEVER owns evidence scoring, weighting, ranking, evaluation, or prioritization.
    """
    evidence_id: str
    reference_id: str
    evidence_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeConfidence:
    """
    Canonical immutable Runtime Confidence artifact.
    Answers "How trustworthy is this Runtime Reasoning artifact?" purely from a structural
    perspective.
    Contains only immutable identifiers and metadata.
    Must NEVER contain/embed:
    - RuntimeObservation
    - RuntimeDecision
    - RuntimeReasoning
    - RuntimeRecommendation
    - RuntimeMetrics
    - Execution, Scheduling, or Provider Health information
    - Latency, Throughput, Retry information
    Must NEVER depend on downstream bounded-context responsibilities.
    """
    confidence_id: str
    reasoning_id: str
    confidence_level: RuntimeConfidenceLevel
    confidence_state: RuntimeConfidenceState
    factors: List[RuntimeConfidenceFactor] = field(default_factory=list)
    evidence: List[RuntimeConfidenceEvidence] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class RuntimeConfidenceInfo:
    """
    Canonical immutable Runtime Confidence metadata.
    Contains identifiers only.
    """
    confidence_id: str
    reasoning_id: str
    confidence_state: RuntimeConfidenceState
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class RuntimeConfidenceResult:
    """
    Immutable transport artifact returned by future Runtime Confidence operations/producers.
    Contains RuntimeConfidenceInfo, summary, and validation.
    Behavior remains outside this bounded context.
    """
    confidence_info: RuntimeConfidenceInfo
    confidence_summary: str
    validation_result: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)
