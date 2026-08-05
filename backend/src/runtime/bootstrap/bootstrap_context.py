import uuid
import datetime
from dataclasses import dataclass, field
from typing import Dict, Any

from .bootstrap_configuration import BootstrapConfiguration


@dataclass
class BootstrapContext:
    """
    Represents temporary bootstrap state.
    This object exists ONLY during bootstrap and should not become Runtime state.
    """
    runtime_identifier: str = field(default_factory=lambda: str(uuid.uuid4()))
    startup_timestamp: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    configuration: BootstrapConfiguration = field(default_factory=BootstrapConfiguration)
    environment: Dict[str, str] = field(default_factory=dict)
    bootstrap_metadata: Dict[str, Any] = field(default_factory=dict)
    execution_context: Dict[str, Any] = field(default_factory=dict)
