from enum import Enum

class TokenType(str, Enum):
    RESET_PASSWORD = "reset"
    CONFIRM_EMAIL = "confirm-email"

class TemplateType(str, Enum):
    VERIFY_EMAIL = "verify-email.html"
    RESET_PASSWORD = "reset-password.html"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

class LinkType(str, Enum):
    OPEN = "open"
    CLOSED = "closed"

class LinkStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    COMPLETED = "completed"

class PaystackWebhookEvent(str, Enum):
    CHARGE_SUCCESS = "charge.success"
    CHARGE_FAILED = "charge.failed"