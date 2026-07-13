from typing import Any, Dict, List, Optional, Type, Union
from pydantic import BaseModel, Field

class AIRequest(BaseModel):
    """Domain-agnostic request model for AI interactions."""
    prompt: str
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    
    # Target schema for structured output (if required)
    response_schema: Optional[Type[BaseModel]] = None
    
    # Multimodal support for future-proofing
    images: List[str] = Field(default_factory=list, description="List of image paths or URLs")
    audio: List[str] = Field(default_factory=list, description="List of audio paths or URLs")
    video: List[str] = Field(default_factory=list, description="List of video paths or URLs")
    documents: List[str] = Field(default_factory=list, description="List of document paths or URLs")
    urls: List[str] = Field(default_factory=list, description="List of web URLs for context")
    
    # Tools support
    tools: List[Any] = Field(default_factory=list)
    
    # Metadata for telemetry or contextual passthrough
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AIResponse(BaseModel):
    """Domain-agnostic response model from AI interactions."""
    text: str = ""
    structured_output: Optional[Union[BaseModel, Dict[str, Any], List[Any]]] = None
    
    # Execution details
    provider: str
    model: str
    latency_ms: int
    
    # Usage statistics
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    
    # Reason for generation finish
    finish_reason: str = "stop"
    
    # The raw unparsed response from the underlying SDK, for debugging
    raw_response: Optional[Any] = None
