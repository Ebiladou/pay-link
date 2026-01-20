from enum import Enum

class TokenType(str, Enum):
    RESET_PASSWORD = "reset"
    CONFIRM_EMAIL = "confirm_email"

class TemplateType(str, Enum):
    VERIFY_EMAIL = "verify-email.html"
    RESET_PASSWORD = "reset-password.html"