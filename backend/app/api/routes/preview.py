"""Preview API routes for TTS testing."""

import logging
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.preview_tts import PreviewTTSService
from app.services.voice_manager import VoiceManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/preview", tags=["preview"])

# Initialize services
preview_service = PreviewTTSService()
voice_manager = VoiceManager()


class TTSPreviewRequest(BaseModel):
    """Request model for TTS preview generation."""
    text: str = Field(..., min_length=1, max_length=500)
    voice_model: str = Field(..., description="Path to voice model")
    length_scale: float = Field(1.0, ge=0.5, le=2.0)
    noise_scale: float = Field(0.667, ge=0.0, le=1.0)
    noise_w: float = Field(0.8, ge=0.0, le=1.0)
    sentence_silence: float = Field(0.35, ge=0.0, le=2.0)


class TTSPreviewResponse(BaseModel):
    """Response model for TTS preview."""
    preview_id: str
    text: str
    audio_url: str
    duration_estimate: float
    voice_model: str
    parameters: Dict[str, float]


class PreviewVoiceInfo(BaseModel):
    """Voice information for preview."""
    model_path: str
    name: str
    dataset: Optional[str] = None
    quality: Optional[str] = None
    file_size_mb: Optional[float] = None
    sample_rate: Optional[int] = None
    language: Optional[str] = None
    gender: Optional[str] = None
    recommended_usage: Optional[List[str]] = None


class PreviewVoicesListResponse(BaseModel):
    """Response for preview voices list."""
    voices: List[PreviewVoiceInfo]
    count: int
    default_voice: str
    recommendations: Dict[str, str]


@router.get("/voices", response_model=PreviewVoicesListResponse)
async def list_preview_voices():
    """List all available voices with preview metadata.
    
    Returns voices with recommendations for different use cases.
    """
    try:
        # Get all available voices
        voices = voice_manager.list_voices()
        
        # Convert to preview format
        preview_voices = []
        for voice in voices:
            # Extract info from path
            voice_path = Path(voice["model_path"])
            parts = voice_path.parts
            
            # Try to extract dataset and quality from path
            dataset = None
            quality = None
            if len(parts) >= 3:
                dataset = parts[-3] if parts[-3] not in ['voices', 'fr', 'en'] else None
                quality = parts[-2] if parts[-2] in ['low', 'medium', 'high'] else None
            
            # Get file size
            file_size_mb = None
            if voice_path.exists():
                file_size_mb = round(voice_path.stat().st_size / (1024 * 1024), 2)
            
            # Determine gender from dataset name
            gender = None
            if dataset:
                if dataset.lower() in ['siwis', 'mls']:
                    gender = 'female'
                elif dataset.lower() in ['tom', 'gilles']:
                    gender = 'male'
            
            # Create voice info
            voice_info = PreviewVoiceInfo(
                model_path=str(voice_path),
                name=voice.get("name", voice_path.stem),
                dataset=dataset,
                quality=quality,
                file_size_mb=file_size_mb,
                sample_rate=voice.get("sample_rate", 22050),
                language=voice.get("language", "fr_FR"),
                gender=gender,
                recommended_usage=voice.get("recommended_usage", ["general"])
            )
            preview_voices.append(voice_info)
        
        # Sort by quality (high -> medium -> low) and name
        quality_order = {'high': 0, 'medium': 1, 'low': 2, None: 3}
        preview_voices.sort(key=lambda v: (quality_order.get(v.quality, 3), v.name))
        
        # Recommendations based on characteristics
        recommendations = {
            "fastest": str(next((v.model_path for v in preview_voices if v.quality == 'low'), preview_voices[0].model_path if preview_voices else "")),
            "highest_quality": str(next((v.model_path for v in preview_voices if v.quality == 'high'), preview_voices[0].model_path if preview_voices else "")),
            "most_natural": str(next((v.model_path for v in preview_voices if v.dataset == 'siwis' and v.quality == 'medium'), preview_voices[0].model_path if preview_voices else "")),
            "french_best": str(next((v.model_path for v in preview_voices if v.language == 'fr_FR' and v.quality in ['medium', 'high']), preview_voices[0].model_path if preview_voices else ""))
        }
        
        return PreviewVoicesListResponse(
            voices=preview_voices,
            count=len(preview_voices),
            default_voice=settings.DEFAULT_VOICE_MODEL if preview_voices else "",
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Failed to list preview voices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tts", response_model=TTSPreviewResponse)
async def generate_preview(request: TTSPreviewRequest):
    """Generate a TTS preview for testing voice settings.
    
    Args:
        request: Preview parameters including text and voice settings
        
    Returns:
        Preview response with audio URL
    """
    try:
        # Validate voice model exists
        voice_path = Path(request.voice_model)
        if not voice_path.exists():
            # Try in voices directory
            voice_path = settings.VOICES_BASE_PATH / request.voice_model
            if not voice_path.exists():
                raise HTTPException(
                    status_code=400,
                    detail=f"Voice model not found: {request.voice_model}"
                )
        
        # Generate preview
        preview_id = str(uuid.uuid4())
        output_path = settings.TEMP_DIR / f"preview_{preview_id}.wav"
        
        # Ensure temp directory exists
        settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        
        # Generate audio
        success = preview_service.generate_preview(
            text=request.text,
            voice_model=str(voice_path),
            output_path=str(output_path),
            length_scale=request.length_scale,
            noise_scale=request.noise_scale,
            noise_w=request.noise_w,
            sentence_silence=request.sentence_silence
        )
        
        if not success or not output_path.exists():
            raise HTTPException(
                status_code=500,
                detail="Failed to generate preview audio"
            )
        
        # Estimate duration (rough calculation)
        char_count = len(request.text)
        words_estimate = char_count / 5  # Average 5 chars per word
        duration_estimate = (words_estimate / 150) * 60 * request.length_scale  # 150 words per minute average
        
        return TTSPreviewResponse(
            preview_id=preview_id,
            text=request.text,
            audio_url=f"/api/preview/audio/{preview_id}",
            duration_estimate=round(duration_estimate, 2),
            voice_model=request.voice_model,
            parameters={
                "length_scale": request.length_scale,
                "noise_scale": request.noise_scale,
                "noise_w": request.noise_w,
                "sentence_silence": request.sentence_silence
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Preview generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audio/{preview_id}")
async def get_preview_audio(preview_id: str):
    """Serve generated preview audio file.
    
    Args:
        preview_id: UUID of the preview
        
    Returns:
        Audio file response
    """
    try:
        # Validate preview ID format
        try:
            uuid.UUID(preview_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid preview ID format")
        
        # Find audio file
        audio_path = settings.TEMP_DIR / f"preview_{preview_id}.wav"
        
        if not audio_path.exists():
            raise HTTPException(status_code=404, detail="Preview audio not found")
        
        return FileResponse(
            path=str(audio_path),
            media_type="audio/wav",
            filename=f"preview_{preview_id}.wav"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to serve preview audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/audio/{preview_id}")
async def delete_preview(preview_id: str):
    """Delete a preview audio file.
    
    Args:
        preview_id: UUID of the preview to delete
        
    Returns:
        Confirmation message
    """
    try:
        # Validate preview ID
        try:
            uuid.UUID(preview_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid preview ID format")
        
        # Find and delete audio file
        audio_path = settings.TEMP_DIR / f"preview_{preview_id}.wav"
        
        if audio_path.exists():
            audio_path.unlink()
            return {"message": f"Preview {preview_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Preview not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete preview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/parameters/defaults")
async def get_default_parameters():
    """Get default TTS parameters with descriptions.
    
    Returns:
        Default parameter values and ranges
    """
    return {
        "parameters": {
            "length_scale": {
                "default": settings.DEFAULT_LENGTH_SCALE,
                "range": [0.5, 2.0],
                "step": 0.1,
                "description": "Speech speed (0.5 = fast, 2.0 = slow)"
            },
            "noise_scale": {
                "default": settings.DEFAULT_NOISE_SCALE,
                "range": [0.0, 1.0],
                "step": 0.1,
                "description": "Voice expressiveness (0 = monotone, 1 = expressive)"
            },
            "noise_w": {
                "default": settings.DEFAULT_NOISE_W,
                "range": [0.0, 1.0],
                "step": 0.1,
                "description": "Phonetic variation"
            },
            "sentence_silence": {
                "default": settings.DEFAULT_SENTENCE_SILENCE,
                "range": [0.0, 2.0],
                "step": 0.05,
                "description": "Pause duration between sentences (seconds)"
            }
        },
        "presets": {
            "audiobook_natural": {
                "length_scale": 1.0,
                "noise_scale": 0.667,
                "noise_w": 0.8,
                "sentence_silence": 0.35,
                "description": "Natural reading pace for audiobooks"
            },
            "news_fast": {
                "length_scale": 0.85,
                "noise_scale": 0.5,
                "noise_w": 0.6,
                "sentence_silence": 0.2,
                "description": "Fast-paced news reading"
            },
            "storytelling": {
                "length_scale": 1.15,
                "noise_scale": 0.8,
                "noise_w": 0.9,
                "sentence_silence": 0.5,
                "description": "Expressive storytelling with pauses"
            }
        }
    }


@router.post("/cleanup")
async def cleanup_old_previews(max_age_hours: int = 24):
    """Clean up old preview files.
    
    Args:
        max_age_hours: Delete files older than this many hours
        
    Returns:
        Cleanup statistics
    """
    try:
        deleted_count = 0
        total_size = 0
        
        if not settings.TEMP_DIR.exists():
            return {
                "deleted": 0,
                "size_freed_mb": 0,
                "message": "No temp directory found"
            }
        
        # Calculate cutoff time
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        # Find and delete old preview files
        for file_path in settings.TEMP_DIR.glob("preview_*.wav"):
            try:
                # Check file age
                file_stat = file_path.stat()
                file_time = datetime.fromtimestamp(file_stat.st_mtime)
                
                if file_time < cutoff_time:
                    total_size += file_stat.st_size
                    file_path.unlink()
                    deleted_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to delete preview file {file_path}: {e}")
                continue
        
        size_freed_mb = round(total_size / (1024 * 1024), 2)
        
        return {
            "deleted": deleted_count,
            "size_freed_mb": size_freed_mb,
            "message": f"Cleaned up {deleted_count} preview files, freed {size_freed_mb} MB"
        }
        
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))