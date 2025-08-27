"""Custom exceptions and error handlers."""

import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

logger = logging.getLogger(__name__)


class AudioBookError(Exception):
    """Base exception for audio book converter."""
    def __init__(self, message: str, error_code: str = "AUDIO_BOOK_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class TextExtractionError(AudioBookError):
    """Exception for text extraction failures."""
    def __init__(self, message: str):
        super().__init__(message, "TEXT_EXTRACTION_ERROR")


class TTSError(AudioBookError):
    """Exception for TTS processing failures."""
    def __init__(self, message: str):
        super().__init__(message, "TTS_ERROR")


class FileProcessingError(AudioBookError):
    """Exception for file processing failures."""
    def __init__(self, message: str):
        super().__init__(message, "FILE_PROCESSING_ERROR")


async def audio_book_exception_handler(request: Request, exc: AudioBookError):
    """Handle custom AudioBook exceptions."""
    logger.error(f"AudioBook error: {exc.error_code} - {exc.message}")
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "type": "audio_book_error"
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.exception(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "error_code": "INTERNAL_ERROR",
            "type": "internal_error"
        }
    )


def add_exception_handlers(app: FastAPI):
    """Add custom exception handlers to FastAPI app."""
    app.add_exception_handler(AudioBookError, audio_book_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)