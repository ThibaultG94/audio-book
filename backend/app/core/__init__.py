"""Core application configuration and utilities."""

from .config import settings
from .exceptions import (
    AudioBookError,
    TextExtractionError, 
    TTSError,
    FileProcessingError
)

__all__ = [
    "settings",
    "AudioBookError",
    "TextExtractionError",
    "TTSError", 
    "FileProcessingError"
]