"""Voice-related Pydantic models and schemas."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.core.config import get_settings


class VoiceTechnicalInfo(BaseModel):
    """Technical details about a voice model."""
    sample_rate: int = Field(..., description="Audio sample rate in Hz")
    num_speakers: int = Field(..., description="Number of speakers in the model")
    model_size: str = Field(..., description="Model size (low, medium, high)")
    architecture: Optional[str] = Field(None, description="Model architecture")


class VoiceQuality(BaseModel):
    """Voice quality metrics."""
    naturalness: int = Field(..., ge=1, le=5, description="Naturalness score (1-5)")
    clarity: int = Field(..., ge=1, le=5, description="Clarity score (1-5)")
    expressiveness: int = Field(..., ge=1, le=5, description="Expressiveness score (1-5)")


class VoiceMetadata(BaseModel):
    """Voice metadata information."""
    name: str = Field(..., description="Human-readable voice name")
    language_code: str = Field(..., description="Language code (e.g., 'fr_FR')")
    gender: Optional[str] = Field(None, description="Speaker gender")
    age: Optional[str] = Field(None, description="Speaker age category")
    dataset: Optional[str] = Field(None, description="Training dataset name")
    description: Optional[str] = Field(None, description="Voice description")
    recommended_usage: List[str] = Field(default_factory=list, description="Recommended use cases")


class Voice(BaseModel):
    """Complete voice model information."""
    id: str = Field(..., description="Unique voice identifier")
    model_path: str = Field(..., description="Path to model file")
    config_path: str = Field(..., description="Path to config file")
    metadata: VoiceMetadata = Field(..., description="Voice metadata")
    technical_info: VoiceTechnicalInfo = Field(..., description="Technical specifications")
    quality: Optional[VoiceQuality] = Field(None, description="Quality metrics")
    available: bool = Field(True, description="Whether voice is available for use")


class VoicesListResponse(BaseModel):
    """Response for voices list endpoint."""
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