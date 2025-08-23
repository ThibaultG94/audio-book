"""TTS preview endpoints for voice testing."""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from app.services.preview_tts import PreviewTTSEngine
from app.core.config import settings
from app.core.exceptions import TTSError

router = APIRouter()

class PreviewRequest(BaseModel):
    """Request for TTS preview generation."""
    text: str = Field(..., min_length=1, max_length=500, description="Text to synthesize (max 500 chars)")
    voice_model: Optional[str] = Field(default=None, description="Voice model to use")
    length_scale: Optional[float] = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed")
    noise_scale: Optional[float] = Field(default=0.667, ge=0.0, le=1.0, description="Voice variation")

class PreviewResponse(BaseModel):
    """Response with preview audio info."""
    preview_id: str
    text: str
    audio_url: str
    duration_estimate: float
    voice_model: str

@router.post("/tts", response_model=PreviewResponse)
async def generate_preview(request: PreviewRequest):
    """
    Generate TTS preview for voice testing.
    
    Args:
        request: Preview generation request
        
    Returns:
        Preview response with audio URL
        
    Raises:
        HTTPException: If TTS generation fails
    """
    try:
        # Initialize preview TTS engine
        preview_engine = PreviewTTSEngine(
            voice_model=request.voice_model,
            length_scale=request.length_scale,
            noise_scale=request.noise_scale,
        )
        
        # Generate unique preview ID
        preview_id = str(uuid.uuid4())
        
        # Create preview audio file
        preview_path = settings.outputs_dir / "previews" / f"{preview_id}.wav"
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate audio
        preview_engine.text_to_wav(request.text, preview_path)
        
        # Calculate estimated duration (rough estimate: ~150 words/minute)
        word_count = len(request.text.split())
        duration_estimate = (word_count / 150) * 60 * request.length_scale
        
        return PreviewResponse(
            preview_id=preview_id,
            text=request.text,
            audio_url=f"/api/preview/audio/{preview_id}",
            duration_estimate=round(duration_estimate, 2),
            voice_model=preview_engine.voice_model
        )
        
    except TTSError as e:
        raise HTTPException(500, f"TTS generation failed: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Preview generation failed: {str(e)}")

@router.get("/audio/{preview_id}")
async def get_preview_audio(preview_id: str):
    """
    Serve preview audio file.
    
    Args:
        preview_id: Unique preview identifier
        
    Returns:
        Audio file for playback
        
    Raises:
        HTTPException: If preview not found
    """
    # Validate preview_id format
    if not preview_id or len(preview_id) < 10:
        raise HTTPException(400, "Invalid preview ID")
    
    # Find preview file
    preview_path = settings.outputs_dir / "previews" / f"{preview_id}.wav"
    
    if not preview_path.exists():
        raise HTTPException(404, "Preview not found")
    
    # Security check: ensure file is within previews directory
    try:
        preview_path.resolve().relative_to((settings.outputs_dir / "previews").resolve())
    except ValueError:
        raise HTTPException(403, "Access denied")
    
    # Return audio file
    return FileResponse(
        path=str(preview_path),
        media_type="audio/wav",
        headers={
            "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
            "Content-Disposition": "inline"  # Play in browser, not download
        }
    )

@router.get("/voices")
async def list_available_voices():
    """
    List available voice models.
    
    Returns:
        List of available voice models with metadata
    """
    voices_dir = settings.voices_dir
    available_voices = []
    
    if voices_dir.exists():
        # Scan for .onnx model files
        for model_file in voices_dir.rglob("*.onnx"):
            # Try to find corresponding .json metadata file
            json_file = model_file.with_suffix(".onnx.json")
            
            voice_info = {
                "model_path": str(model_file.relative_to(voices_dir)),
                "name": model_file.stem,
                "full_path": str(model_file)
            }
            
            # Load metadata if available
            if json_file.exists():
                try:
                    import json
                    with open(json_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    voice_info.update({
                        "language": metadata.get("language", {}),
                        "dataset": metadata.get("dataset", "unknown"),
                        "quality": metadata.get("audio", {}).get("quality", "unknown"),
                        "sample_rate": metadata.get("audio", {}).get("sample_rate", 22050)
                    })
                except Exception:
                    pass  # Ignore metadata parsing errors
            
            available_voices.append(voice_info)
    
    return {
        "voices": available_voices,
        "default_voice": settings.voice_model,
        "count": len(available_voices)
    }

@router.delete("/audio/{preview_id}")
async def delete_preview(preview_id: str):
    """
    Delete preview audio file to save storage.
    
    Args:
        preview_id: Preview to delete
        
    Returns:
        Success confirmation
    """
    if not preview_id or len(preview_id) < 10:
        raise HTTPException(400, "Invalid preview ID")
    
    preview_path = settings.outputs_dir / "previews" / f"{preview_id}.wav"
    
    if preview_path.exists():
        try:
            preview_path.unlink()
            return {"message": "Preview deleted successfully"}
        except Exception as e:
            raise HTTPException(500, f"Failed to delete preview: {str(e)}")
    else:
        return {"message": "Preview not found (may already be deleted)"}

# Cleanup endpoint for old previews (optional)
@router.post("/cleanup")
async def cleanup_old_previews(max_age_hours: int = 24):
    """
    Clean up preview files older than specified hours.
    
    Args:
        max_age_hours: Maximum age in hours before cleanup
        
    Returns:
        Cleanup statistics
    """
    import time
    
    previews_dir = settings.outputs_dir / "previews"
    if not previews_dir.exists():
        return {"deleted": 0, "message": "No previews directory"}
    
    current_time = time.time()
    deleted_count = 0
    
    for preview_file in previews_dir.glob("*.wav"):
        # Check file age
        file_age_seconds = current_time - preview_file.stat().st_mtime
        file_age_hours = file_age_seconds / 3600
        
        if file_age_hours > max_age_hours:
            try:
                preview_file.unlink()
                deleted_count += 1
            except Exception:
                pass  # Ignore deletion errors
    
    return {
        "deleted": deleted_count,
        "message": f"Cleaned up {deleted_count} preview files older than {max_age_hours}h"
    }