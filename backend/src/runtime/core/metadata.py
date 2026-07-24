import uuid
from dataclasses import dataclass, field

@dataclass(frozen=True)
class RuntimeMetadata:
    """
    Descriptive metadata representing the Runtime instance.
    
    This object is intentionally lightweight and read-only.
    It exists to describe the Runtime (e.g., version, identifier).
    It must NEVER contain Runtime Configuration, Provider Configuration,
    Hardware Configuration, or mutable Runtime Settings.
    """
    runtime_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: str = "0.1.0"
    build_profile: str = "local"
