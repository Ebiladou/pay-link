from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import secrets

class Settings(BaseSettings):
	# database configurations
	REDIRECT_URI: Optional[str] = "localhost:8080"
	DATABASE_NAME: Optional[str] = None
	DATABASE_URL: Optional[str] = None

	# JWT
	SECRET_KEY: str = secrets.token_urlsafe(32)
	algorithm: str = "HS256"
	access_token_expires_min: int


	PAYSTACK_SECRET_KEY: str = ""

	# Redis configuration for task queue
	REDIS_URL: Optional[str] = "redis://localhost:6379"

	model_config = SettingsConfigDict(env_file=".env")

settings = Settings()