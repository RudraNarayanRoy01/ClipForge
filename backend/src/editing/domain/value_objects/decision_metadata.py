from dataclasses import dataclass

@dataclass(frozen=True)
class DecisionMetadata:
    """
    Contextual information about an editing decision.
    Immutable value object representing the 'why' and 'how important' of a decision.
    """
    confidence: float
    priority: int
    rationale: str
    source: str
