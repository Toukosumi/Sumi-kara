"""Logger utility module."""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = "SumiKara", log_dir: str = "./logs") -> logging.Logger:
    """Setup and return a logger with file and console output.

    Args:
        name: Logger name
        log_dir: Directory to store log files

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create log directory if not exists
    os.makedirs(log_dir, exist_ok=True)

    # Log file path
    log_file = os.path.join(log_dir, "app.log")

    # File handler - Rotating, DEBUG level
    # maxBytes: 单个日志文件最大 5MB
    # backupCount: 保留 5 个备份文件
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_format)

    # Console handler - INFO level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_format)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Default logger instance
logger = setup_logger()
