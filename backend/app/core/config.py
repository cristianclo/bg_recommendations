from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List


class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "Board Game Recommendations System"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/bg_recommendations",
        description="PostgreSQL database URL"
    )
    DATABASE_URL_ASYNC: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/bg_recommendations",
        description="Async PostgreSQL database URL"
    )
    
    # Security
    SECRET_KEY: str = Field(
        ...,
        min_length=32,
        description="Secret key for JWT token generation (must be at least 32 characters)"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
