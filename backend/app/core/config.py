"""Application configuration."""

from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Audio Book Converter"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    # Paths - use Path objects
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    STORAGE_BASE_PATH: Path = BASE_DIR / "storage"
    UPLOAD_DIR: Path = STORAGE_BASE_PATH / "uploads"
    OUTPUT_DIR: Path = STORAGE_BASE_PATH / "outputs"
    TEMP_DIR: Path = STORAGE_BASE_PATH / "temp"
    VOICES_BASE_PATH: Path = BASE_DIR / "voices"
    
    # File Processing
    MAX_FILE_SIZE: int = 52428800  # 50MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".epub", ".txt", ".docx", ".rtf"]
    
    # TTS Configuration
    DEFAULT_VOICE_MODEL: str = "fr_FR-siwis-low"
    DEFAULT_LENGTH_SCALE: float = 1.0
    DEFAULT_NOISE_SCALE: float = 0.667
    DEFAULT_NOISE_W: float = 0.8
    DEFAULT_SENTENCE_SILENCE: float = 0.35
    DEFAULT_PAUSE_BETWEEN_BLOCKS: float = 1.0
    
    # Text Processing
    MAX_CHUNK_CHARS: int = 1500
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()