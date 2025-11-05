from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = Field(default="LLM Code Navigator", description="Name of the project")
    BACKEND_DIR: str = Field(default="work", description="Directory to analyze for Python files")
    ALLOWED_ORIGINS: List[str] = Field(
        default_factory=lambda: ["http://localhost", "http://localhost:3000"],
        description="Allowed CORS origins"
    )
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Security settings
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, description="Maximum file size in bytes (10MB)")
    ALLOWED_FILE_EXTENSIONS: List[str] = Field(
        default_factory=lambda: [".py", ".pyx", ".pyi"],
        description="Allowed file extensions for analysis"
    )
    
    # PMD settings
    PMD_ENABLED: bool = Field(default=True, description="Enable PMD static analysis")
    PMD_TIMEOUT: int = Field(default=30, description="PMD analysis timeout in seconds")

    @field_validator('BACKEND_DIR')
    @classmethod
    def validate_backend_dir(cls, v: str) -> str:
        """Validate that backend directory exists and is accessible."""
        # Handle relative paths from project root
        if not os.path.isabs(v):
            # Get the project root (parent of backend directory)
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            v = os.path.join(current_dir, v)
        
        path = Path(v)
        if not path.exists():
            # Create directory if it doesn't exist
            try:
                path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                # If we can't create it, just return the path - it might be created later
                print(f"Warning: Cannot create backend directory {v}: {e}")
                return str(path.resolve())
        
        if path.exists() and not path.is_dir():
            raise ValueError(f"Backend directory {v} is not a directory")
        
        # Convert to absolute path for security
        return str(path.resolve())

    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()

    @field_validator('MAX_FILE_SIZE')
    @classmethod
    def validate_max_file_size(cls, v: int) -> int:
        """Validate maximum file size."""
        if v <= 0:
            raise ValueError("Maximum file size must be positive")
        if v > 100 * 1024 * 1024:  # 100MB limit
            raise ValueError("Maximum file size cannot exceed 100MB")
        return v

    @field_validator('ALLOWED_FILE_EXTENSIONS')
    @classmethod
    def validate_file_extensions(cls, v: List[str]) -> List[str]:
        """Validate file extensions."""
        if not v:
            raise ValueError("At least one file extension must be allowed")
        
        # Ensure extensions start with dot
        validated = []
        for ext in v:
            if not ext.startswith('.'):
                ext = '.' + ext
            validated.append(ext.lower())
        
        return validated

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
