import redis
from typing import Optional
from app.core.logger import logger
from app.core.config import settings

QUEUE_EMAIL = "email_tasks"

class RedisQueue:    
    def __init__(self, host: str, port: int, password: str, db: int = 0):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self._client: Optional[redis.Redis] = None

    def get_client(self) -> redis.Redis:
        if self._client is None:
            try:
                self._client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_keepalive=True
                )
                self._client.ping()
                logger.info("Redis connected")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
        
        return self._client

    def close(self) -> None:
        if self._client:
            self._client.close()
            logger.info("Redis disconnected")

redis_queue = RedisQueue(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD
)