"""Centralised logging setup for RDRS."""
import sys
from loguru import logger
from app.core.config import load_config


def setup_logging():
    """Configure loguru with separate log files for each category."""
    config = load_config()
    log_dir = config.get('log_dir', './logs')

    logger.remove()
    logger.add(sys.stdout, level="INFO")
    logger.add(f"{log_dir}/system.log", rotation="10 MB", level="INFO")
    logger.add(f"{log_dir}/events.log", rotation="10 MB", level="DEBUG")
    logger.add(f"{log_dir}/alerts.log", rotation="10 MB", level="WARNING")
    logger.add(f"{log_dir}/errors.log", rotation="10 MB", level="ERROR")
    logger.add(f"{log_dir}/audit.log", rotation="10 MB", level="INFO",
               filter=lambda record: "AUDIT" in record["message"])
    return logger
