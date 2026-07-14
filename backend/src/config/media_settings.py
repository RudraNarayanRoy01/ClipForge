from pydantic_settings import BaseSettings
from pydantic import Field

class MediaSettings(BaseSettings):
    """Configuration settings for media processing infrastructure."""
    
    ffmpeg_executable_path: str = Field(default="ffmpeg", description="Path to the FFmpeg executable")
    ffprobe_executable_path: str = Field(default="ffprobe", description="Path to the FFprobe executable")
    process_timeout: int = Field(default=300, description="Default timeout in seconds for media processing operations")

    class Config:
        env_file = ".env"
        extra = "ignore"
