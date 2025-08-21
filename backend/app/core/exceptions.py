"""Custom exceptions for the application."""


class AudioBookError(Exception):
    """Base exception for audio book application."""
    pass


class TextExtractionError(AudioBookError):
    """Raised when text extraction from documents fails."""
    pass


class TTSError(AudioBookError):
    """Raised when TTS synthesis fails."""
    pass


class FileProcessingError(AudioBookError):
    """Raised when file processing fails."""
    pass
