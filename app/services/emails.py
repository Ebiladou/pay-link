from datetime import datetime
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader
from app.core.config import settings
from app.core.enum import TemplateType
from app.core.logger import logger
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

class EmailService:
    def __init__(self, api_key: str, environment: str, from_email: str = "noreply@paylink.co", from_name: str = "Paylink", templates_dir: str = "app/templates"):
        self._api_key = api_key
        self._environment = environment
        self._mail_from = from_email
        self._mail_from_name = from_name
        self._client = sendgrid.SendGridAPIClient(api_key=self._api_key)

        self._template_env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True
        )

    def _render_template(self, template_name: TemplateType, variables: Dict[str, Any]):
        try:
            html_template = self._template_env.get_template(template_name.value)
            return html_template.render(**variables)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {e}")
            raise

    async def send_email(self, template_name: TemplateType, subject: str, email: str, name: str, variables: Optional[Dict[str, Any]] = None):
        try:
            template_variables = {
                "name": name,
                **(variables or {})
            }

            html_content = self._render_template(template_name, template_variables)

            mail = Mail(
                from_email=Email(self._mail_from, self._mail_from_name),
                to_emails=To(email, name),
                subject=subject,
                html_content=Content("text/html", html_content)
            )

            if self._environment == "prod":
                response = self._client.client.mail.send.post(request_body=mail.get())
                if response.status_code == 202:
                    logger.info(f"Email '{template_name}' sent successfully to {email}.")
                    return True
                else:
                    logger.error(f"Failed to send email '{template_name}'. Status: {response.status_code}, Body: {response.body}")
                    return False
            else:
                logger.info(f"[{self._environment}] Email '{template_name}' would be sent to {email}")
                if variables:
                    logger.info(f"Variables: {variables}")
                return True

        except Exception as e:
            logger.error(f"Failed to send email '{template_name}': {e}")
            return False


email_service = EmailService(
    api_key=settings.SENDGRID_API_KEY,
    environment=settings.ENVIRONMENT
)