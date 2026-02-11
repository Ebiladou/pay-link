from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
	# database configurations
	ENVIRONMENT: str
	REDIRECT_URI: Optional[str] = "localhost:8080"
	DATABASE_URL: str

	# postgres
	POSTGRES_USER: str
	POSTGRES_PASSWORD: str
	POSTGRES_DB: str

	# JWT
	SECRET_KEY: str
	ALGORITHM: str = "HS256"
	ACCESS_TOKEN_EXPIRE_MINUTES: int

	REDIS_URL: str = "redis://localhost:6379"

	MAILERSEND_KEY: str

	# paystack
	PAYSTACK_PUBLIC_KEY: str
	PAYSTACK_SECRET_KEY: str

	model_config = SettingsConfigDict(env_file=".env")

settings = Settings()