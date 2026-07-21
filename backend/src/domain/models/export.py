from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any


class ExportStatus(str, Enum):
    """
    Represents the lifecycle state of an export operation.
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class ExportSettings:
    """
    Encapsulates the configuration required to export or deliver a rendered artifact.
    Contains delivery intent and destination logic, but no rendering concerns.
    """
    destination: str
    overwrite_existing: bool = False
    naming_strategy: Optional[str] = None


@dataclass(frozen=True)
class ExportRequest:
    """
    Represents the canonical request to deliver an already-produced media artifact.
    """
    source_media_location: str
    settings: ExportSettings


@dataclass(frozen=True)
class ExportResult:
    """
    Represents the outcome of an export operation using domain information only.
    """
    status: ExportStatus
    exported_location: Optional[str] = None
    export_metadata: Dict[str, Any] = field(default_factory=dict)
    message: Optional[str] = None
