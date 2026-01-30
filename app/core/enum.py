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

class PaystackChannel(str, Enum):
    CARD = "card"
    BANK = "bank"
    APPLE_PAY = "apple_pay"
    USSD = "ussd"
    MOBILE_MONEY = "mobile_money"
    BANK_TRANSFER = "bank_transfer"