from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "LLM Code Navigator"
    BACKEND_DIR: str = "/app/backend"
    ALLOWED_ORIGINS: list = ["http://localhost", "http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()