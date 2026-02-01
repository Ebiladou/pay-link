import redis
from typing import Optional
from app.core.logger import logger

QUEUE_EMAIL = "email_tasks"

class RedisQueue:    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
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

redis_queue = RedisQueue()