"""Logger utility module."""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# 延迟导入 path_utils，避免循环依赖问题
# 注意：logger 初始化在模块级别，此时 global_config 应该已经加载
def _get_log_dir() -> str:
    """Get log directory, fallback to ./logs if not configured."""
    try:
        from utils.path_utils import get_log_dir
        return get_log_dir()
    except Exception:
        # 如果导入失败（比如在打包后的环境），使用默认路径
        return "./logs"


def setup_logger(name: str = "SumiKara", log_dir: str = None) -> logging.Logger:
    """Setup and return a logger with file and console output.

    Args:
        name: Logger name
        log_dir: Directory to store log files (default: use path_utils.get_log_dir())

    Returns:
        Configured logger instance
    """
    # 如果未指定 log_dir，则使用 path_utils 获取
    if log_dir is None:
        log_dir = _get_log_dir()

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
