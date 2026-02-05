"""Logging configuration and setup."""

import sys
import logging
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors."""
    
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record):
        """Format log record with color."""
        level = record.levelname
        color = self.COLORS.get(level, "")
        record.levelname = f"{color}{level: <8}{self.RESET}"
        return super().format(record)


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Configure and return logger instance.
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    # TODO: Load log level from config/environment
    # TODO: Setup structured logging for production
    
    logger = logging.getLogger(name)
    logger.setLevel(level.upper())
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level.upper())
    
    console_formatter = ColoredFormatter(
        "%(levelname)s | %(name)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(log_dir / "crawler.log")
    file_handler.setLevel(level.upper())
    
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger
