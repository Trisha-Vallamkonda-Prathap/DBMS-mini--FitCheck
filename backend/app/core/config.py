from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "FitCheck Fit Intelligence System"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # MySQL Configuration
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "fitcheck"
    MYSQL_USER: str = "fitcheck_user"
    MYSQL_PASSWORD: str = "fitcheck_password"
    DATABASE_URL: str = ""

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: str, values) -> str:
        if isinstance(v, str) and v:
            return v
        data = values.data
        return (
            f"mysql+pymysql://{data.get('MYSQL_USER')}:{data.get('MYSQL_PASSWORD')}"
            f"@{data.get('MYSQL_HOST')}:{data.get('MYSQL_PORT')}/{data.get('MYSQL_DATABASE')}"
        )

    # Redis Stack Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    REDIS_INDEX_NAME: str = "fit_review_idx"

    # Embedding Model Configuration
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Security & Tokens
    SECRET_KEY: str = "fitcheck_development_secret_key_minimum_32_characters_long_12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
