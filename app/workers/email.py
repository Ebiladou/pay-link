import json
import asyncio
from typing import Dict, Any, Optional

import pika
from app.services.queue import rabbitmq, QUEUE_EMAIL
from app.core.enum import TemplateType
from app.services.emails import email_service
from app.core.logger import logger

async def queue_email(
    template_name: TemplateType,
    subject: str,
    email: str,
    name: str,
    variables: Optional[Dict[str, Any]] = None,
) -> bool:
    try:
        channel = rabbitmq.get_channel()
        channel.queue_declare(queue=QUEUE_EMAIL, durable=True)
        
        message = {
            "template_name": template_name.value,
            "subject": subject,
            "email": email,
            "name": name,
            "variables": variables or {},
        }
        
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_EMAIL,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
        )
        
        logger.info(f"Email queued for {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to queue email: {e}")
        return False


# Consumer Worker

def process_email_message(channel, method, properties, body):
    """Process a single email message from the queue"""
    try:
        message = json.loads(body)
        logger.info(f"Processing email for {message['email']}")
        
        # Run async email send in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                email_service.send_email(
                    template_name=TemplateType(message["template_name"]),
                    subject=message["subject"],
                    email=message["email"],
                    name=message["name"],
                    variables=message.get("variables"),
                )
            )
            
            if result:
                logger.info(f"Email sent to {message['email']}")
                channel.basic_ack(delivery_tag=method.delivery_tag)
            else:
                logger.warning(f"Email failed for {message['email']}, requeuing...")
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error processing email: {e}")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_email_worker():
    """Start consuming email tasks from queue"""
    try:
        channel = rabbitmq.get_channel()
        channel.queue_declare(queue=QUEUE_EMAIL, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=QUEUE_EMAIL, on_message_callback=process_email_message)
        
        logger.info(f"Email worker started, listening on {QUEUE_EMAIL}")
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Email worker interrupted")
    except Exception as e:
        logger.error(f"Email worker error: {e}")
        raise
