from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class LifecycleDecision(str, Enum):
    """
    Decisions that the KnowledgeLifecyclePolicy can return.
    """
    KEEP = "KEEP"
    REFRESH_REQUIRED = "REFRESH_REQUIRED"
    INVALID = "INVALID"
    INCOMPATIBLE = "INCOMPATIBLE"


class LifecycleEvaluation(BaseModel):
    """
    The result of a lifecycle policy evaluation.
    """
    decision: LifecycleDecision = Field(description="The decision made by the policy")
    reason: str = Field(description="A provider-independent reason for the decision")

    class Config:
        frozen = True


class LifecycleEvaluationCriteria(BaseModel):
    """
    The criteria used to evaluate the lifecycle of a knowledge snapshot.
    """
    expected_schema_version: str = Field(description="The currently supported schema version")
    expected_knowledge_version: str = Field(description="The currently supported knowledge version")
    current_source_version: str = Field(description="The current version/hash of the underlying source media")
    max_age_seconds: Optional[int] = Field(default=None, description="Optional maximum age in seconds for a snapshot")

    class Config:
        frozen = True
