from enum import Enum

class TokenType(str, Enum):
    RESET_PASSWORD = "reset"
    CONFIRM_EMAIL = "confirm_email"
    SIGNIN = "signin"