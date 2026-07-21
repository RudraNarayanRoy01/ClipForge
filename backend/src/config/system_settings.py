from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal

class SystemSettings(BaseSettings):
    """Configuration settings for system-wide application variables."""
    
    environment: Literal["development", "testing", "production"] = Field(
        default="development", 
        description="The environment the application is running in."
    )
    cors_origins: str = Field(
        default="", 
        description="Comma-separated list of allowed CORS origins for production."
    )
    db_path: str = Field(
        default="clipping_platform.db", 
        description="Path to the SQLite database file."
    )

    class Config:
        env_file = ".env"
        extra = "ignore"
