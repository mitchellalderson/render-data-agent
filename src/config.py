"""Configuration management for the ICP Analysis Dashboard."""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    
    host: str
    port: int
    database: str
    user: str
    password: str
    url: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Create database config from environment variables."""
        url = os.getenv("DATABASE_URL")
        
        return cls(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            database=os.getenv("POSTGRES_DB", "render_data"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", ""),
            url=url
        )
    
    def get_connection_string(self) -> str:
        """Get the database connection string."""
        if self.url:
            return self.url
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class LLMConfig:
    """LLM API configuration settings."""
    
    api_key: str
    model: str
    provider: str = "openai"
    
    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Create LLM config from environment variables."""
        return cls(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            model=os.getenv("LLM_MODEL", "gpt-4-turbo-preview"),
            provider=os.getenv("LLM_PROVIDER", "openai")
        )


@dataclass
class AppConfig:
    """Application configuration settings."""
    
    title: str
    max_upload_size_mb: int
    debug_mode: bool
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create app config from environment variables."""
        return cls(
            title=os.getenv("APP_TITLE", "ICP Analysis Dashboard"),
            max_upload_size_mb=int(os.getenv("MAX_UPLOAD_SIZE_MB", "50")),
            debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true"
        )


class Config:
    """Main configuration class."""
    
    def __init__(self):
        self.database = DatabaseConfig.from_env()
        self.llm = LLMConfig.from_env()
        self.app = AppConfig.from_env()
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a configuration value by key.
        
        Args:
            key: Environment variable key
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        return os.getenv(key, default)
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        # Check database config
        if not self.database.password and not self.database.url:
            errors.append("Database password or DATABASE_URL is required")
        
        # Check LLM config
        if not self.llm.api_key:
            errors.append("OpenAI API key is required")
        
        return errors


# Global config instance
config = Config()

