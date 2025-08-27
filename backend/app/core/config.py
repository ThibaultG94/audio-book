"""Application configuration management."""

import os
from pathlib import Path
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable loading."""
    
    # Application
    APP_NAME: str = "TTS Audio Book Converter"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # File Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    VOICES_BASE_PATH: Path = BASE_DIR / "voices"
    STORAGE_BASE_PATH: Path = BASE_DIR / "storage"
    UPLOAD_DIR: Path = STORAGE_BASE_PATH / "uploads"
    OUTPUT_DIR: Path = STORAGE_BASE_PATH / "outputs"
    TEMP_DIR: Path = STORAGE_BASE_PATH / "temp"
    
    # TTS Configuration
    DEFAULT_VOICE_MODEL: str = "fr_FR-siwis-low"
    PIPER_EXECUTABLE: str = "piper"
    
    # Default TTS Parameters
    DEFAULT_LENGTH_SCALE: float = 1.0
    DEFAULT_NOISE_SCALE: float = 0.667
    DEFAULT_NOISE_W: float = 0.8
    DEFAULT_SENTENCE_SILENCE: float = 0.35
    DEFAULT_PAUSE_BETWEEN_BLOCKS: float = 0.35
    
    # File Processing
    MAX_FILE_SIZE: int = 52_428_800  # 50MB
    MAX_CHUNK_CHARS: int = 1500
    ALLOWED_EXTENSIONS: set[str] = {".pdf", ".epub"}
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }

    @property
    def outputs_dir(self) -> Path:
        """Alias for OUTPUT_DIR."""
        return self.OUTPUT_DIR
    
    @property
    def voices_dir(self) -> Path:
        """Alias for VOICES_BASE_PATH."""
        return self.VOICES_BASE_PATH
    
    @property
    def voice_model(self) -> str:
        """Alias for DEFAULT_VOICE_MODEL."""
        return self.DEFAULT_VOICE_MODEL
    
    @property
    def uploads_dir(self) -> Path:
        """Alias for UPLOAD_DIR."""
        return self.UPLOAD_DIR
    
    @property
    def allowed_extensions(self) -> set[str]:
        """Alias for ALLOWED_EXTENSIONS."""
        return self.ALLOWED_EXTENSIONS
    
    @property
    def pause_between_blocks(self) -> float:
        """Alias for DEFAULT_PAUSE_BETWEEN_BLOCKS."""
        return self.DEFAULT_PAUSE_BETWEEN_BLOCKS
    
    @property
    def length_scale(self) -> float:
        """Alias for DEFAULT_LENGTH_SCALE."""
        return self.DEFAULT_LENGTH_SCALE
    
    @property
    def noise_scale(self) -> float:
        """Alias for DEFAULT_NOISE_SCALE."""
        return self.DEFAULT_NOISE_SCALE
    
    @property
    def noise_w(self) -> float:
        """Alias for DEFAULT_NOISE_W."""
        return self.DEFAULT_NOISE_W
    
    @property
    def sentence_silence(self) -> float:
        """Alias for DEFAULT_SENTENCE_SILENCE."""
        return self.DEFAULT_SENTENCE_SILENCE

    def model_post_init(self, __context) -> None:
        """Ensure required directories exist."""
        for path in [self.STORAGE_BASE_PATH, self.UPLOAD_DIR, self.OUTPUT_DIR, self.TEMP_DIR]:
            path.mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Alias for backward compatibility and easy access
settings = get_settings()