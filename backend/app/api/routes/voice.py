"""Voice management API routes."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.voice_manager import VoiceManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/voice", tags=["voice"])

# Initialize voice manager
voice_manager = VoiceManager()


class VoiceListResponse(BaseModel):
    """Response model for voice list."""
    voices: list
    count: int
    default_voice: Optional[str] = None


@router.get("/list", response_model=VoiceListResponse)
async def list_voices(
    language: Optional[str] = None,
    quality: Optional[str] = None
):
    """List all available voice models.
    
    Args:
        language: Filter by language code
        quality: Filter by quality level
        
    Returns:
        List of available voices
    """
    try:
        voices = voice_manager.list_voices(language=language, quality=quality)
        default = voice_manager.get_default_voice()
        
        return VoiceListResponse(
            voices=voices,
            count=len(voices),
            default_voice=default
        )
        
    except Exception as e:
        logger.error(f"Failed to list voices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{voice_id}")
async def get_voice_details(voice_id: str):
    """Get detailed information about a specific voice.
    
    Args:
        voice_id: Voice identifier
        
    Returns:
        Voice details
    """
    try:
        voice = voice_manager.get_voice(voice_id)
        
        if not voice:
            raise HTTPException(status_code=404, detail=f"Voice not found: {voice_id}")
        
        return voice
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get voice details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validate/{voice_id}")
async def validate_voice(voice_id: str):
    """Validate a voice model.
    
    Args:
        voice_id: Voice identifier
        
    Returns:
        Validation results
    """
    try:
        voice = voice_manager.get_voice(voice_id)
        
        if not voice:
            raise HTTPException(status_code=404, detail=f"Voice not found: {voice_id}")
        
        validation = voice_manager.validate_voice(voice["model_path"])
        
        return {
            "voice_id": voice_id,
            "valid": validation["valid"],
            "model_file": validation["model_file"],
            "config_file": voice.get("config_path"),
            "config_valid": validation.get("config_valid", False),
            "issues": validation["issues"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate voice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh")
async def refresh_voices():
    """Refresh the voice cache.
    
    Returns:
        Confirmation message
    """
    try:
        voice_manager.refresh_cache()
        voices = voice_manager.list_voices()
        
        return {
            "message": "Voice cache refreshed successfully",
            "voices_found": len(voices)
        }
        
    except Exception as e:
        logger.error(f"Failed to refresh voices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))