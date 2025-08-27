"""Voice models and schemas for TTS configuration."""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class VoiceQuality(str, Enum):
    """Voice quality levels."""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"


class VoiceTechnicalInfo(BaseModel):
    """Technical voice specifications."""
    sample_rate: int = Field(..., description="Audio sample rate in Hz")
    num_speakers: int = Field(..., description="Number of speakers (1 for single voice)")
    quality: VoiceQuality = Field(..., description="Voice quality level")
    audio_quality: str = Field(..., description="Audio quality description")


class VoiceMetadata(BaseModel):
    """Voice metadata information."""
    name: str = Field(..., description="Voice display name")
    language: str = Field(..., description="Language code (e.g., 'fr_FR')")
    dataset: str = Field(..., description="Dataset name used for training")
    version: str = Field("1.0", description="Voice model version")
    description: Optional[str] = Field(None, description="Voice description")
    technical: VoiceTechnicalInfo = Field(..., description="Technical specifications")
    recommended_usage: Optional[List[str]] = Field(default_factory=list, description="Recommended use cases")


class Voice(BaseModel):
    """Complete voice model information."""
    id: str = Field(..., description="Unique voice identifier")
    name: str = Field(..., description="Voice display name")
    language: str = Field(..., description="Language code")
    gender: Optional[str] = Field(None, description="Voice gender")
    age: Optional[str] = Field(None, description="Approximate age category")
    quality: VoiceQuality = Field(..., description="Voice quality level")
    file_path: str = Field(..., description="Path to voice model file")
    config_path: str = Field(..., description="Path to voice config file")
    metadata: VoiceMetadata = Field(..., description="Complete voice metadata")
    is_available: bool = Field(True, description="Whether voice model files are accessible")


class VoicesListResponse(BaseModel):
    """Response for voice listing endpoint."""
    voices: List[Voice] = Field(..., description="Available voices")
    count: int = Field(..., description="Total number of voices")
    default_voice: Optional[str] = Field(None, description="Default voice ID")


class TTSPreviewRequest(BaseModel):
    """Request for TTS preview generation."""
    text: str = Field(..., min_length=1, max_length=500, description="Text to synthesize")
    voice_model: str = Field(..., description="Voice model ID to use")
    length_scale: float = Field(1.0, ge=0.5, le=2.0, description="Speech speed (1.0 = normal)")
    noise_scale: float = Field(0.667, ge=0.0, le=1.0, description="Voice variation amount")
    noise_w: float = Field(0.8, ge=0.0, le=1.0, description="Phoneme width variation")
    sentence_silence: float = Field(0.35, ge=0.0, le=2.0, description="Pause between sentences")


class TTSPreviewResponse(BaseModel):
    """Response for TTS preview generation."""
    audio_url: str = Field(..., description="URL to download generated audio")
    duration_seconds: Optional[float] = Field(None, description="Audio duration")
    text_length: int = Field(..., description="Number of characters processed")
    voice_used: str = Field(..., description="Voice model ID used")


# backend/app/services/voice_service.py
"""Voice management service for TTS operations."""

import os
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from app.core.config import get_settings
from app.models.voice import Voice, VoiceMetadata, VoiceTechnicalInfo, VoiceQuality, VoicesListResponse

logger = logging.getLogger(__name__)


class VoiceService:
    """Service for managing TTS voices."""
    
    def __init__(self):
        self.settings = get_settings()
        self.voices_dir = Path(self.settings.VOICES_BASE_PATH)
        self._voices_cache: Optional[List[Voice]] = None
    
    def get_available_voices(self) -> VoicesListResponse:
        """Get list of all available voices with metadata."""
        if self._voices_cache is None:
            self._voices_cache = self._scan_voices()
        
        return VoicesListResponse(
            voices=self._voices_cache,
            count=len(self._voices_cache),
            default_voice=self.settings.DEFAULT_VOICE_MODEL
        )
    
    def get_voice_by_id(self, voice_id: str) -> Optional[Voice]:
        """Get specific voice by ID."""
        voices_response = self.get_available_voices()
        for voice in voices_response.voices:
            if voice.id == voice_id:
                return voice
        return None
    
    def is_voice_available(self, voice_id: str) -> bool:
        """Check if voice model files are accessible."""
        voice = self.get_voice_by_id(voice_id)
        if not voice:
            return False
        
        return (
            Path(voice.file_path).exists() and 
            Path(voice.config_path).exists()
        )
    
    def _scan_voices(self) -> List[Voice]:
        """Scan voices directory and build voice list."""
        voices = []
        
        if not self.voices_dir.exists():
            logger.warning(f"Voices directory not found: {self.voices_dir}")
            return voices
        
        # Scan for .onnx files recursively
        for onnx_file in self.voices_dir.rglob("*.onnx"):
            config_file = onnx_file.with_suffix(".onnx.json")
            
            if not config_file.exists():
                logger.warning(f"Config file missing for {onnx_file}")
                continue
            
            try:
                voice = self._create_voice_from_files(onnx_file, config_file)
                if voice:
                    voices.append(voice)
            except Exception as e:
                logger.error(f"Failed to process voice {onnx_file}: {e}")
        
        logger.info(f"Found {len(voices)} available voices")
        return voices
    
    def _create_voice_from_files(self, onnx_path: Path, config_path: Path) -> Optional[Voice]:
        """Create Voice object from model files."""
        try:
            # Load voice configuration
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Extract basic info
            voice_id = self._generate_voice_id(onnx_path)
            
            # Parse metadata from config
            metadata = self._parse_voice_metadata(config)
            
            # Determine quality from path or config
            quality = self._determine_quality(onnx_path, config)
            
            return Voice(
                id=voice_id,
                name=metadata.name,
                language=metadata.language,
                gender=self._extract_gender(metadata.name, metadata.description),
                age=None,  # Not available in current configs
                quality=quality,
                file_path=str(onnx_path),
                config_path=str(config_path),
                metadata=metadata,
                is_available=onnx_path.exists() and config_path.exists()
            )
        
        except Exception as e:
            logger.error(f"Failed to create voice from {onnx_path}: {e}")
            return None
    
    def _generate_voice_id(self, onnx_path: Path) -> str:
        """Generate unique voice ID from file path."""
        # Use relative path from voices directory as ID
        try:
            relative_path = onnx_path.relative_to(self.voices_dir)
            # Convert path to ID: voices/fr/fr_FR/siwis/low/model.onnx -> fr_FR-siwis-low
            parts = relative_path.parts[:-1]  # Exclude filename
            if len(parts) >= 3:
                return f"{parts[1]}-{parts[2]}-{parts[3]}"
            else:
                return onnx_path.stem
        except ValueError:
            return onnx_path.stem
    
    def _parse_voice_metadata(self, config: Dict[str, Any]) -> VoiceMetadata:
        """Parse voice metadata from config file."""
        # Default values
        name = config.get("name", "Unknown Voice")
        language = config.get("language", {}).get("code", "unknown")
        dataset = config.get("dataset", "unknown")
        
        # Technical info
        audio = config.get("audio", {})
        technical = VoiceTechnicalInfo(
            sample_rate=audio.get("sample_rate", 22050),
            num_speakers=config.get("num_speakers", 1),
            quality=VoiceQuality.LOW,  # Will be determined later
            audio_quality="Standard"
        )
        
        # Recommended usage (if available)
        recommended_usage = config.get("recommended_usage", [])
        if not recommended_usage:
            # Infer from voice characteristics
            if "audiobook" in name.lower() or "reader" in name.lower():
                recommended_usage = ["audiobook", "long_form"]
            elif "news" in name.lower():
                recommended_usage = ["news", "formal"]
            else:
                recommended_usage = ["general"]
        
        return VoiceMetadata(
            name=name,
            language=language,
            dataset=dataset,
            version=config.get("version", "1.0"),
            description=config.get("description"),
            technical=technical,
            recommended_usage=recommended_usage
        )
    
    def _determine_quality(self, onnx_path: Path, config: Dict[str, Any]) -> VoiceQuality:
        """Determine voice quality from path or config."""
        path_str = str(onnx_path).lower()
        
        if "high" in path_str:
            return VoiceQuality.HIGH
        elif "medium" in path_str:
            return VoiceQuality.MEDIUM
        elif "low" in path_str:
            return VoiceQuality.LOW
        else:
            # Fallback: check file size or other indicators
            try:
                file_size = onnx_path.stat().st_size
                if file_size > 50_000_000:  # > 50MB
                    return VoiceQuality.HIGH
                elif file_size > 20_000_000:  # > 20MB
                    return VoiceQuality.MEDIUM
                else:
                    return VoiceQuality.LOW
            except:
                return VoiceQuality.LOW
    
    def _extract_gender(self, name: str, description: Optional[str]) -> Optional[str]:
        """Extract gender from voice name or description."""
        text = f"{name} {description or ''}".lower()
        
        if any(word in text for word in ["female", "woman", "femme", "feminine"]):
            return "female"
        elif any(word in text for word in ["male", "man", "homme", "masculine"]):
            return "male"
        
        return None


# backend/app/api/routes/preview.py
"""Preview routes for voice testing and TTS preview generation."""

import os
import tempfile
import uuid
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse

from app.core.config import get_settings
from app.services.voice_service import VoiceService
from app.services.tts_engine import TTSEngine
from app.models.voice import VoicesListResponse, TTSPreviewRequest, TTSPreviewResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/preview", tags=["preview"])


def get_voice_service() -> VoiceService:
    """Get voice service dependency."""
    return VoiceService()


def get_tts_engine() -> TTSEngine:
    """Get TTS engine dependency."""
    return TTSEngine()


@router.get("/voices", response_model=VoicesListResponse)
async def get_available_voices(
    voice_service: VoiceService = Depends(get_voice_service)
) -> VoicesListResponse:
    """Get list of available TTS voices with metadata.
    
    Returns:
        VoicesListResponse: List of available voices with technical details
        
    Raises:
        HTTPException: 500 if voice scanning fails
    """
    try:
        voices_response = voice_service.get_available_voices()
        
        if voices_response.count == 0:
            logger.warning("No voices found in voices directory")
            
        return voices_response
        
    except Exception as e:
        logger.error(f"Failed to get available voices: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to scan available voices: {str(e)}"
        )


@router.post("/tts", response_model=TTSPreviewResponse)
async def generate_tts_preview(
    request: TTSPreviewRequest,
    background_tasks: BackgroundTasks,
    voice_service: VoiceService = Depends(get_voice_service),
    tts_engine: TTSEngine = Depends(get_tts_engine)
) -> TTSPreviewResponse:
    """Generate TTS audio preview for voice testing.
    
    Args:
        request: TTS generation parameters
        background_tasks: For cleanup tasks
        voice_service: Voice management service
        tts_engine: TTS processing engine
        
    Returns:
        TTSPreviewResponse: URL to generated audio file
        
    Raises:
        HTTPException: 400 for validation errors, 500 for processing errors
    """
    try:
        # Validate voice exists
        voice = voice_service.get_voice_by_id(request.voice_model)
        if not voice:
            raise HTTPException(
                status_code=400,
                detail=f"Voice model not found: {request.voice_model}"
            )
        
        if not voice.is_available:
            raise HTTPException(
                status_code=400,
                detail=f"Voice model files not accessible: {request.voice_model}"
            )
        
        # Generate unique filename for preview
        preview_id = str(uuid.uuid4())
        output_filename = f"preview_{preview_id}.wav"
        
        settings = get_settings()
        output_path = Path(settings.TEMP_DIR) / output_filename
        
        # Ensure temp directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate TTS audio
        duration = await tts_engine.synthesize_text(
            text=request.text,
            voice_path=voice.file_path,
            output_path=str(output_path),
            length_scale=request.length_scale,
            noise_scale=request.noise_scale,
            noise_w=request.noise_w,
            sentence_silence=request.sentence_silence
        )
        
        # Schedule cleanup after 10 minutes
        background_tasks.add_task(
            cleanup_temp_file,
            output_path,
            delay_seconds=600
        )
        
        # Return download URL
        audio_url = f"/api/preview/audio/{preview_id}"
        
        return TTSPreviewResponse(
            audio_url=audio_url,
            duration_seconds=duration,
            text_length=len(request.text),
            voice_used=request.voice_model
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS preview generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate TTS preview: {str(e)}"
        )


@router.get("/audio/{preview_id}")
async def download_preview_audio(preview_id: str) -> FileResponse:
    """Download generated preview audio file.
    
    Args:
        preview_id: Unique preview identifier
        
    Returns:
        FileResponse: Audio file download
        
    Raises:
        HTTPException: 404 if file not found
    """
    try:
        settings = get_settings()
        audio_path = Path(settings.TEMP_DIR) / f"preview_{preview_id}.wav"
        
        if not audio_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Preview audio file not found or expired"
            )
        
        return FileResponse(
            path=str(audio_path),
            media_type="audio/wav",
            filename=f"voice_preview_{preview_id}.wav",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to serve preview audio {preview_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve preview audio"
        )


async def cleanup_temp_file(file_path: Path, delay_seconds: int = 0) -> None:
    """Clean up temporary files after delay.
    
    Args:
        file_path: Path to file to delete
        delay_seconds: Delay before deletion
    """
    import asyncio
    
    if delay_seconds > 0:
        await asyncio.sleep(delay_seconds)
    
    try:
        if file_path.exists():
            file_path.unlink()
            logger.debug(f"Cleaned up temp file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup temp file {file_path}: {e}")


# backend/app/core/config.py - Add missing settings
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


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()