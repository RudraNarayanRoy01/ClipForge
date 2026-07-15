from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class TranscriptionSettings(BaseSettings):
    """Configuration settings for transcription providers (e.g. Whisper)."""
    
    transcription_model: str = Field(default="base", description="Faster-Whisper model name or path")
    transcription_device: str = Field(default="auto", description="Device to use (cpu, cuda, auto)")
    transcription_compute_type: str = Field(default="default", description="Compute type (default, int8, float16)")
    transcription_language: Optional[str] = Field(default=None, description="Default language code for transcription")
    transcription_beam_size: int = Field(default=5, description="Beam size for transcription")

    class Config:
        env_file = ".env"
        extra = "ignore"
