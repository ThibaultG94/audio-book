"""Audio file serving API routes."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/audio", tags=["audio"])


@router.get("/{job_id}")
async def get_audio_file(job_id: str):
    """Stream generated audio file.
    
    Args:
        job_id: Conversion job identifier
        
    Returns:
        Audio file stream
    """
    try:
        # Try different formats
        for ext in ['.wav', '.mp3']:
            audio_path = settings.OUTPUT_DIR / f"{job_id}{ext}"
            if audio_path.exists():
                return FileResponse(
                    path=str(audio_path),
                    media_type=f"audio/{ext[1:]}",
                    filename=f"audiobook_{job_id}{ext}"
                )
        
        raise HTTPException(status_code=404, detail="Audio file not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to serve audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/download")
async def download_audio_file(job_id: str):
    """Download generated audio file.
    
    Args:
        job_id: Conversion job identifier
        
    Returns:
        Audio file download
    """
    try:
        # Try different formats
        for ext in ['.wav', '.mp3']:
            audio_path = settings.OUTPUT_DIR / f"{job_id}{ext}"
            if audio_path.exists():
                return FileResponse(
                    path=str(audio_path),
                    media_type="application/octet-stream",
                    filename=f"audiobook_{job_id}{ext}",
                    headers={
                        "Content-Disposition": f"attachment; filename=audiobook_{job_id}{ext}"
                    }
                )
        
        raise HTTPException(status_code=404, detail="Audio file not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{job_id}")
async def delete_audio_file(job_id: str):
    """Delete generated audio file.
    
    Args:
        job_id: Conversion job identifier
        
    Returns:
        Confirmation message
    """
    try:
        deleted = False
        
        # Try different formats
        for ext in ['.wav', '.mp3']:
            audio_path = settings.OUTPUT_DIR / f"{job_id}{ext}"
            if audio_path.exists():
                audio_path.unlink()
                deleted = True
                logger.info(f"Deleted audio file: {audio_path}")
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        return {"message": f"Audio file for job {job_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))