from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, Literal

class AISettings(BaseSettings):
    ai_provider: Literal["ollama", "gemini", "openai", "anthropic", "openrouter"] = "ollama"
    
    # Ollama Specific
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "gemma4:latest"
    
    # Generic AI settings
    ai_timeout_seconds: int = Field(default=60, gt=0)
    ai_max_retries: int = Field(default=3, ge=0)
    ai_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    ai_max_tokens: Optional[int] = None
    ai_stream_responses: bool = False
    ai_context_length: Optional[int] = None
    ai_keep_alive: str = "5m"
    
    # Telemetry and Logging
    ai_log_prompts: bool = False
    ai_log_responses: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"
