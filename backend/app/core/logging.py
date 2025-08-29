# backend/app/core/logging.py
"""Enhanced logging configuration for debugging upload issues."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.core.config import settings


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m',     # Reset
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # Add color to level name
        record.levelname = f"{log_color}{record.levelname}{reset_color}"
        
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    enable_colors: bool = True
) -> None:
    """Setup application logging with enhanced formatting."""
    
    # Convert string level to logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatters
    detailed_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    )
    
    console_formatter = ColoredFormatter(detailed_format) if enable_colors else logging.Formatter(detailed_format)
    file_formatter = logging.Formatter(detailed_format)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always debug level for file
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    configure_loggers(numeric_level)


def configure_loggers(level: int) -> None:
    """Configure specific loggers with appropriate levels."""
    
    # Application loggers
    app_loggers = [
        "app",
        "app.api.routes.upload",
        "app.api.routes.convert", 
        "app.services.file_processor",
        "app.services.tts_engine",
    ]
    
    for logger_name in app_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
    
    # Third-party loggers (more restrictive)
    third_party_loggers = {
        "uvicorn": logging.INFO,
        "uvicorn.access": logging.WARNING,
        "fastapi": logging.INFO,
        "httpx": logging.WARNING,
    }
    
    for logger_name, logger_level in third_party_loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(max(level, logger_level))


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)


# Initialize logging based on settings
def init_app_logging() -> None:
    """Initialize application logging."""
    log_level = "DEBUG" if settings.DEBUG else "INFO"
    log_file = settings.STORAGE_BASE_PATH / "logs" / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    
    setup_logging(
        level=log_level,
        log_file=log_file,
        enable_colors=True
    )
    
    logger = get_logger(__name__)
    logger.info(f"Logging initialized - Level: {log_level}, File: {log_file}")