from typing import List, Optional
from pydantic import BaseModel, Field

class PromptMetadata(BaseModel):
    """
    Metadata describing a prompt, extracted from JSON-frontmatter.
    """
    name: str = Field(description="Unique identifier or name of the prompt")
    description: str = Field(default="", description="Human-readable description")
    variables: List[str] = Field(default_factory=list, description="List of required {{variables}} in the body")
    default_temperature: Optional[float] = Field(default=None, description="Recommended temperature for this prompt")
    
    # Optional descriptive metadata
    expected_output: Optional[str] = Field(default=None, description="Description of the expected format/output")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization (e.g. 'classification', 'extraction')")

class PromptTemplate(BaseModel):
    """
    Holds the parsed metadata and the raw markdown body of a prompt.
    """
    metadata: PromptMetadata
    body: str

class RenderedPrompt(BaseModel):
    """
    Encapsulates the final rendered prompt string alongside its source metadata.
    Produced by the PromptManager and consumed by the AI Orchestrator.
    """
    prompt_identifier: str
    text: str
    metadata: PromptMetadata
