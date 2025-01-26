from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = Field(default="LLM Code Navigator")
    BACKEND_DIR: str = Field(default="/app/work")
    ALLOWED_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost", "http://localhost:3000"])

    class Config:
        env_file = ".env"


settings = Settings()
