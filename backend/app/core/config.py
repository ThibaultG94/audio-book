"""Application configuration with correct voice model paths."""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "TTS Audio Book Converter"
    debug: bool = False
    
    # Paths - All paths relative to backend/ directory
    voices_dir: Path = Path("voices")
    storage_dir: Path = Path("storage")
    uploads_dir: Path = Path("storage/uploads")
    outputs_dir: Path = Path("storage/outputs")
    
    # TTS Configuration - Auto-detect best available voice
    voice_model: str = "voices/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx"  # Try medium first
    length_scale: float = 1.0
    noise_scale: float = 0.667
    noise_w: float = 0.8
    sentence_silence: float = 0.35
    pause_between_blocks: float = 0.35
    
    # Text Processing
    max_chunk_chars: int = 1500
    
    # File Upload
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_extensions: set[str] = {".pdf", ".epub"}
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-detect best available voice model at startup
        self.voice_model = self._find_best_voice_model()
    
    def _find_best_voice_model(self) -> str:
        """Find the best available voice model in priority order."""
        
        # Priority order: medium quality French voices first, then fallback
        voice_candidates = [
            "voices/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx",
            "voices/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx", 
            "voices/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx",  # Original default
            "voices/fr/fr_FR/tom/medium/fr_FR-tom-medium.onnx",
        ]
        
        for candidate in voice_candidates:
            candidate_path = Path(candidate)
            if candidate_path.exists() and candidate_path.is_file():
                print(f"🎤 Selected voice model: {candidate}")
                return candidate
        
        # Fallback: search for any .onnx file
        if self.voices_dir.exists():
            for onnx_file in self.voices_dir.rglob("*.onnx"):
                relative_path = str(onnx_file)
                print(f"🎤 Fallback voice model: {relative_path}")
                return relative_path
        
        # Final fallback to original default (even if it doesn't exist)
        print(f"⚠️  No voice models found, using default: {voice_candidates[2]}")
        return voice_candidates[2]
    
    class Config:
        env_file = ".env"


settings = Settings()

# Startup voice model information
if __name__ == "__main__":
    import os
    print("🔍 Voice Model Configuration:")
    print(f"  Selected model: {settings.voice_model}")
    print(f"  Model exists: {Path(settings.voice_model).exists()}")
    print(f"  Voices directory: {settings.voices_dir}")
    print(f"  Voices dir exists: {settings.voices_dir.exists()}")
    
    if settings.voices_dir.exists():
        onnx_files = list(settings.voices_dir.rglob("*.onnx"))
        print(f"  Available models ({len(onnx_files)}):")
        for i, model in enumerate(onnx_files[:5]):  # Show first 5
            size = model.stat().st_size // (1024*1024) if model.exists() else 0
            print(f"    {i+1}. {model} ({size}MB)")
        if len(onnx_files) > 5:
            print(f"    ... and {len(onnx_files)-5} more")
    else:
        print("  ❌ Voices directory not found")