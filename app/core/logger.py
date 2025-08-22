# app/core/logger.py
import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from app.config import AppSettings

app_settings = AppSettings()
# Log level (dev vs prod via ENV)
LOG_LEVEL = logging.DEBUG if app_settings.APP_MODE == "dev" else logging.INFO

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Directory for log files
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(name: str = "app") -> logging.Logger:
    """Set up and return a logger instance usable across the app."""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    if not logger.handlers:  # avoid duplicates in reload mode
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        logger.addHandler(console_handler)

        # Rotating file handler (max 5MB, keep 5 backups)
        file_handler = RotatingFileHandler(
            os.path.join(LOG_DIR, "app.log"),
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        logger.addHandler(file_handler)

        # Silence noisy loggers
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.INFO)

    return logger
