"""Application configuration."""

from pydantic import BaseModel
from typing import Optional
from pathlib import Path


class Settings(BaseModel):
    """Application settings."""
    
    # App info
    app_name: str = "Audio Book Converter"
    version: str = "1.0.0"
    debug: bool = True
    
    # API settings
    api_prefix: str = "/api"
    allowed_origins: list = ["http://localhost:3000", "http://localhost:3001"]
    
    # File settings
    max_file_size: int = 52428800  # 50MB
    allowed_extensions: list = [".pdf", ".epub", ".txt"]
    
    # TTS settings
    default_voice: str = "en_US-amy-medium"
    voice_model: str = "en_US-amy-medium.onnx"
    voice_config: str = "en_US-amy-medium.onnx.json"
    length_scale: float = 1.0
    noise_scale: float = 0.667
    sentence_silence: float = 0.35
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent
    storage_dir: Path = base_dir / "storage"
    uploads_dir: Path = storage_dir / "uploads"
    outputs_dir: Path = storage_dir / "outputs"
    temp_dir: Path = storage_dir / "temp"
    voices_dir: Path = base_dir / "voices"
    
    # Processing
    max_chunk_chars: int = 1500
    processing_timeout: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create global settings instance
settings = Settings()

# Ensure directories exist
settings.storage_dir.mkdir(parents=True, exist_ok=True)
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
settings.outputs_dir.mkdir(parents=True, exist_ok=True)
settings.temp_dir.mkdir(parents=True, exist_ok=True)
settings.voices_dir.mkdir(parents=True, exist_ok=True)
