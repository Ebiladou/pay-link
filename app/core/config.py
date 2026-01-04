from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import secrets

class Settings(BaseSettings):
	# database configurations
	ENVIRONMENT: str
	REDIRECT_URI: Optional[str] = "localhost:8080"
	DATABASE_URL: Optional[str] = None

	# JWT
	SECRET_KEY: str = secrets.token_urlsafe(32)
	ALGORITHM: str = "HS256"
	ACCESS_TOKEN_EXPIRE_MINUTES: int

	# Redis configuration for task queue
	REDIS_URL: Optional[str] = "redis://localhost:6379"

	model_config = SettingsConfigDict(env_file=".env")

settings = Settings()