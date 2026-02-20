import json
import asyncio
from typing import Dict, Any, Optional
from app.services.queue import redis_queue, QUEUE_EMAIL
from app.core.enum import TemplateType
from app.services.emails import email_service
from app.core.logger import logger

MAX_RETRIES = 5

async def queue_email(template_name: TemplateType, subject: str, email: str, name: str, variables: Optional[Dict[str, Any]] = None):
    try:
        client = redis_queue.get_client()
        
        message = {
            "template_name": template_name.value,
            "subject": subject,
            "email": email,
            "name": name,
            "variables": variables or {},
            "retry_count": 0,
        }
        
        client.rpush(QUEUE_EMAIL, json.dumps(message))
        logger.info(f"Email queued for {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to queue email: {e}")
        return False

def process_email_message(message: str):
    try:
        data = json.loads(message)
        retry_count = data.get("retry_count", 0)
        email = data["email"]
      
        logger.info(f"Processing email for {email} (attempt {retry_count + 1}/{MAX_RETRIES})")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                email_service.send_email(
                    template_name=TemplateType(data["template_name"]),
                    subject=data["subject"],
                    email=data["email"],
                    name=data["name"],
                    variables=data.get("variables"),
                )
            )
            
            if result:
                logger.info(f"Email sent to {data['email']}")
            else:
                if retry_count < MAX_RETRIES - 1:
                    logger.warning(f"Email failed for {email}, requeuing (attempt {retry_count + 1}/{MAX_RETRIES})...")
                    data["retry_count"] = retry_count + 1
                    redis_queue.get_client().rpush(QUEUE_EMAIL, json.dumps(data))
                else:
                    logger.error(f"Email permanently failed for {email} after {MAX_RETRIES} attempts. Dropping.")
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error processing email: {e}")

        try:
            data = json.loads(message)
            retry_count = data.get("retry_count", 0)
            if retry_count < MAX_RETRIES - 1:
                data["retry_count"] = retry_count + 1
                redis_queue.get_client().rpush(QUEUE_EMAIL, json.dumps(data))
            else:
                logger.error(f"Email permanently failed after {MAX_RETRIES} attempts. Dropping.")
        except Exception:
            logger.error("Could not requeue message — malformed payload. Dropping.")


def start_email_worker():
    try:
        client = redis_queue.get_client()
        
        logger.info(f"Email worker started, listening on {QUEUE_EMAIL}")
    
        while True:
            message = client.blpop(QUEUE_EMAIL, timeout=30)
            
            if message:
                _, message_content = message
                process_email_message(message_content)
                
    except KeyboardInterrupt:
        logger.info("Email worker interrupted")
    except Exception as e:
        logger.error(f"Email worker error: {e}")
        raise