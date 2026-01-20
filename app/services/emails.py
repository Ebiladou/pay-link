from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
from app.core.config import settings
from app.core.enum import TemplateType
from mailersend import Email
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, api_key: str = settings.MAILERSEND_KEY, mail_from: str = "test-pzkmgq7yorml059v.mlsender.net", mail_from_name: str = "PayLink", environment: str = settings.ENVIRONMENT, templates_dir: str = "app/templates"):
        self._api_key = api_key
        self._mail_from = mail_from
        self._mail_from_name = mail_from_name
        self._environment = environment
        self._mailer = Email
        
        self._template_env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True
        )

    def _render_template(self, template_name: TemplateType, variables: Dict[str, Any]) -> str:
        try:
            # Render HTML template
            html_template = self._template_env.get_template(template_name.value)
            html_content = html_template.render(**variables)
            
            return html_content
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {e}")
            raise

    async def send_email(self, template_name: TemplateType, subject: str, email: str, name: str, variables: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send an email using a template.
        
        Args:
            template_name: Name of the template (e.g., 'verify_email', 'reset_password')
            subject: Email subject line
            email: Recipient email address
            name: Recipient name
            variables: Additional variables to pass to the template
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Prepare template variables
            template_variables = {
                "name": name,
                **(variables or {})
            }
            
            # Render templates
            html_content = self._render_template(template_name, template_variables)
            
            # Prepare mail
            mail_from = {
                "email": self._mail_from,
                "name": self._mail_from_name,
            }
            
            recipients = [{"email": email, "name": name}]

            mail_body = {
                "from_email": mail_from,
                "to": recipients,
                "subject": subject,
                "html": html_content,
            }

           # self._mailer.send(mail_body)
            
            # Send email
            if self._environment == "prod":
                response = self._mailer.send(mail_body)
                logger.info(f"Email '{template_name}' sent to {email}")
                return True
            else:
                logger.info(f"Email '{template_name}' would be sent to {email}")
                logger.info(f"Subject: {subject}")
                if variables:
                    logger.info(f"Variables: {variables}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send email '{template_name}': {e}")
            return False
        
email_service = EmailService()