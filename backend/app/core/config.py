"""
Application configuration using Pydantic Settings.
Loads configuration from environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "SamarthanSathi"
    ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
