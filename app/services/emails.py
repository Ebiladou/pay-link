from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
from app.core.config import settings
from app.core.enum import TemplateType
from app.core.logger import logger
from mailersend import MailerSendClient
from mailersend.models.email import EmailRequest, EmailContact

class EmailService:
    def __init__(self, api_key: str, environment: str, mail_from: str = "", mail_from_name: str = "PayLink", templates_dir: str = "app/templates"):
        self._api_key = api_key
        self._environment = environment
        self._mail_from = mail_from
        self._mail_from_name = mail_from_name
        self._client = MailerSendClient(api_key=self._api_key)
        
        self._template_env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True
        )

    def _render_template(self, template_name: TemplateType, variables: Dict[str, Any]) -> str:
        try:
            html_template = self._template_env.get_template(template_name.value)
            html_content = html_template.render(**variables)
            
            return html_content
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {e}")
            raise

    async def send_email(self, template_name: TemplateType, subject: str, email: str, name: str, variables: Optional[Dict[str, Any]] = None) -> bool:
        try:
            # Prepare template variables
            template_variables = {
                "name": name,
                **(variables or {})
            }
            
            # Render templates
            html_content = self._render_template(template_name, template_variables)
            
            from_contact = EmailContact(email=self._mail_from, name=self._mail_from_name)
            to_contacts = [EmailContact(email=email, name=name)]
            
            email_request = EmailRequest(
                from_email=from_contact,
                to=to_contacts,
                subject=subject,
                html=html_content,
            )
            
            if self._environment == "prod":
                response = self._client.emails.send(email_request)
                if response.status_code == 202:
                    logger.info(f"Email sent successfully.")
                    return True
                else:
                    logger.error(f"Failed to send email '{template_name}'. Error: {response.data}")
                    return False
            else:
                logger.info(f"Email '{template_name}' would be sent to {email}")
                if variables:
                    logger.info(f"Variables: {variables}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send email '{template_name}': {e}")
            return False
        
email_service = EmailService(
    api_key = settings.MAILERSEND_KEY,
    environment = settings.ENVIRONMENT
)