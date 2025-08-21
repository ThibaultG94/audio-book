"""Application configuration and settings."""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "TTS Audio Book Converter"
    debug: bool = False
    
    # Paths
    voices_dir: Path = Path("voices")
    storage_dir: Path = Path("storage")
    uploads_dir: Path = Path("storage/uploads")
    outputs_dir: Path = Path("storage/outputs")
    
    # TTS Configuration
    voice_model: str = "voices/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx"
    length_scale: float = 1.0  # 0.9 = faster, 1.1 = slower
    noise_scale: float = 0.667
    noise_w: float = 0.8
    sentence_silence: float = 0.35  # pause between sentences
    pause_between_blocks: float = 0.35  # manual pause between blocks
    
    # Text Processing
    max_chunk_chars: int = 1500
    
    # File Upload
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_extensions: set[str] = {".pdf", ".epub"}
    
    class Config:
        env_file = ".env"


settings = Settings()