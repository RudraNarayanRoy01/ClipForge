import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Union
from datetime import datetime, timezone


class KnowledgeCategory(Enum):
    """
    Classifies the type of knowledge.
    """
    CREATOR = auto()
    PLATFORM = auto()
    CAMPAIGN = auto()
    RESTRICTION = auto()
    REWARD = auto()
    WORKFLOW = auto()


class KnowledgeSource(Enum):
    """
    Represents where knowledge originated.
    """
    CAMPAIGN_EVALUATION = auto()
    HISTORICAL_AGGREGATION = auto()
    MANUAL_ENTRY = auto()


class KnowledgeConfidence(Enum):
    """
    Represents confidence using deterministic domain values.
    """
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()


@dataclass(frozen=True)
class CampaignEvaluationReference:
    """Reference to the specific campaign evaluation that originated this knowledge."""
    evaluation_id: uuid.UUID
    campaign_name: str


@dataclass(frozen=True)
class HistoricalAggregationReference:
    """Reference to a historical aggregation process that produced this knowledge."""
    aggregation_period: str
    description: str


@dataclass(frozen=True)
class ManualKnowledgeReference:
    """Reference for manually inputted knowledge."""
    author: str
    context: str


# Type alias for the allowed domain-level source references
KnowledgeReference = Union[
    CampaignEvaluationReference,
    HistoricalAggregationReference,
    ManualKnowledgeReference
]


@dataclass(frozen=True)
class KnowledgeEvidence:
    """
    Represents traceability. Knowledge should always remain explainable.
    Explains where knowledge originated without coupling to persistence.
    """
    source: KnowledgeSource
    description: str
    reference: KnowledgeReference


@dataclass(frozen=True)
class KnowledgeEntry:
    """
    Represents one persistent unit of organizational knowledge.

    IMPORTANT: This represents durable business knowledge, not copied campaign facts.

    Examples of durable knowledge:
    - Creator consistently pays above average.
    - Platform frequently requires original audio.
    - Certain restriction patterns commonly lead to rejection.

    Examples that are NOT knowledge (these are just facts):
    - Reward = $20
    - Deadline = Tomorrow
    - Platform = TikTok
    """
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    category: KnowledgeCategory
    subject: str
    value: str
    confidence: KnowledgeConfidence
    evidence: List[KnowledgeEvidence] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
