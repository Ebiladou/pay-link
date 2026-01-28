import logging
import os
import sys
from logging.handlers import RotatingFileHandler

APP_ENV = os.getenv("ENVIRONMENT", "dev") 

# Create a logger
logger = logging.getLogger("paylink")

# Dynamically set log level based on environment
if APP_ENV == "dev":
    logger.setLevel(logging.DEBUG)
elif APP_ENV == "prod":
    logger.setLevel(logging.WARNING)
else:
    logger.setLevel(logging.INFO)

# Prevent duplicate handlers from being added if logger is imported multiple times
if not logger.hasHandlers():
    # Create a console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logger.level)

    # Create a rotating file handler (writes logs to a file with rotation)
    log_file = os.getenv("LOG_FILE", "logs/paylink.log")
    os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)

    # Set a formatter
    log_format = os.getenv(
        "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    formatter = logging.Formatter(log_format)

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)