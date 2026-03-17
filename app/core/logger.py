import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from app.core.config import settings

APP_ENV = settings.ENVIRONMENT

logger = logging.getLogger("paylink")

if APP_ENV == "dev":
    logger.setLevel(logging.DEBUG)
elif APP_ENV == "prod":
    logger.setLevel(logging.WARNING)
else:
    logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logger.level)

    log_file = os.getenv("LOG_FILE", "logs/paylink.log")
    os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)

    log_format = os.getenv(
        "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    formatter = logging.Formatter(log_format)

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)