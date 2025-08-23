# backend/app/core/config.py - Fix voice model path
"""Application configuration with correct voice model paths."""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "TTS Audio Book Converter"
    debug: bool = False
    
    # Paths - IMPORTANT: All paths relative to backend/ directory
    voices_dir: Path = Path("voices")  # backend/voices/
    storage_dir: Path = Path("storage")  # backend/storage/
    uploads_dir: Path = Path("storage/uploads")  # backend/storage/uploads/
    outputs_dir: Path = Path("storage/outputs")  # backend/storage/outputs/
    
    # TTS Configuration - FULL PATH from backend/ directory
    voice_model: str = "voices/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx"  # ⚠️ Fixed path!
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

# Debug voice model path on startup
if __name__ == "__main__":
    import os
    print("🔍 Voice model configuration:")
    print(f"  Settings voice_model: {settings.voice_model}")
    print(f"  Current working directory: {os.getcwd()}")
    print(f"  Full voice model path: {Path(settings.voice_model).resolve()}")
    print(f"  Voice model exists: {Path(settings.voice_model).exists()}")
    
    # List available voice models
    if settings.voices_dir.exists():
        print("📂 Available voice models:")
        for model_file in settings.voices_dir.rglob("*.onnx"):
            print(f"  - {model_file}")
    else:
        print(f"❌ Voices directory not found: {settings.voices_dir}")