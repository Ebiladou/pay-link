from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
	# database configurations
	ENVIRONMENT: str
	REDIRECT_URI: Optional[str] = "localhost:8080"
	DATABASE_URL: Optional[str] = None

	# postgres
	POSTGRES_USER: str
	POSTGRES_PASSWORD: str
	POSTGRES_DB: str

	# JWT
	SECRET_KEY: str
	ALGORITHM: str = "HS256"
	ACCESS_TOKEN_EXPIRE_MINUTES: int

	REDIS_URL: Optional[str] = "redis://localhost:6379"
	RESEND_SECRET_KEY: str

	MAILERSEND_KEY: str

	# rabbitmq
	RABBITMQ_USER: str = "guest"
	RABBITMQ_PASSWORD: str = "guest"

	model_config = SettingsConfigDict(env_file=".env")

settings = Settings()