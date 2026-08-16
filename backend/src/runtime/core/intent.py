from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class ExecutionIntent:
    """
    The immutable declarative intent to execute a resolved capability.
    
    This represents 'what work is being requested' for a known capability.
    It is produced after a capability is successfully resolved.
    
    The payload is intentionally opaque (Any) at this boundary because no 
    existing Runtime-core, provider-neutral payload contract was identified 
    that is suitable for this abstraction. The ExecutionIntent object is 
    structurally immutable, though it does not introduce a recursive 
    immutability framework for arbitrary payload contents.
    
    The output_contract is a descriptive identifier (e.g., 'ExtractionSummarySchema') 
    and does not imply schema registration, instantiation, or validation at this layer.
    """
    capability_id: str
    payload: Any
    output_contract: str | None = None
