import pika
from typing import Optional
from app.core.logger import logger

QUEUE_EMAIL = "email_tasks"

class RabbitMQ:    
    def __init__(self, host: str = "localhost", port: int = 5672):
        self.host = host
        self.port = port
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None

    def get_channel(self) -> pika.adapters.blocking_connection.BlockingChannel:
        if self._connection is None or self._connection.is_closed:
            credentials = pika.PlainCredentials("guest", "guest")
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                connection_attempts=3,
                retry_delay=2
            )
            self._connection = pika.BlockingConnection(parameters)
            logger.info("RabbitMQ connected")
        
        if self._channel is None or self._channel.is_closed:
            self._channel = self._connection.channel()
        
        return self._channel

    def close(self) -> None:
        if self._connection and not self._connection.is_closed:
            self._connection.close()
            logger.info("RabbitMQ disconnected")

rabbitmq = RabbitMQ()
