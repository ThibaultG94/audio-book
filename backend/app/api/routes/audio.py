"""Audio file serving endpoints."""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from pathlib import Path
import mimetypes
import os

from app.core.config import settings

router = APIRouter()

@router.get("/{job_id}")
async def get_audio_file(job_id: str):
    """
    Serve generated audio file for download.
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        Audio file as download
        
    Raises:
        HTTPException: If file not found or invalid job_id
    """
    # Validate job_id format (basic UUID check)
    if not job_id or len(job_id) < 10:
        raise HTTPException(400, "Invalid job ID")
    
    # Construct file path
    audio_file_path = settings.outputs_dir / f"{job_id}.wav"
    
    # Check if file exists
    if not audio_file_path.exists() or not audio_file_path.is_file():
        raise HTTPException(404, "Audio file not found")
    
    # Security check: ensure file is within outputs directory
    try:
        audio_file_path.resolve().relative_to(settings.outputs_dir.resolve())
    except ValueError:
        raise HTTPException(403, "Access denied")
    
    # Get file info
    file_size = audio_file_path.stat().st_size
    media_type = mimetypes.guess_type(str(audio_file_path))[0] or "audio/wav"
    
    # Return file for download
    return FileResponse(
        path=str(audio_file_path),
        media_type=media_type,
        filename=f"audiobook_{job_id}.wav",
        headers={
            "Content-Length": str(file_size),
            "Content-Disposition": f"attachment; filename=audiobook_{job_id}.wav"
        }
    )

@router.head("/{job_id}")
async def check_audio_file(job_id: str):
    """
    Check if audio file exists without downloading.
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        HTTP headers with file info or 404
    """
    # Validate job_id
    if not job_id or len(job_id) < 10:
        raise HTTPException(400, "Invalid job ID")
    
    # Check file existence
    audio_file_path = settings.outputs_dir / f"{job_id}.wav"
    
    if not audio_file_path.exists():
        raise HTTPException(404, "Audio file not found")
    
    # Security check
    try:
        audio_file_path.resolve().relative_to(settings.outputs_dir.resolve())
    except ValueError:
        raise HTTPException(403, "Access denied")
    
    # Return headers only
    file_size = audio_file_path.stat().st_size
    
    return Response(
        headers={
            "Content-Type": "audio/wav",
            "Content-Length": str(file_size),
            "Accept-Ranges": "bytes"
        }
    )

@router.get("/info/{job_id}")
async def get_audio_info(job_id: str):
    """
    Get metadata about generated audio file.
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        JSON with file metadata
    """
    # Validate job_id
    if not job_id or len(job_id) < 10:
        raise HTTPException(400, "Invalid job ID")
    
    # Check file
    audio_file_path = settings.outputs_dir / f"{job_id}.wav"
    
    if not audio_file_path.exists():
        raise HTTPException(404, "Audio file not found")
    
    # Security check
    try:
        audio_file_path.resolve().relative_to(settings.outputs_dir.resolve())
    except ValueError:
        raise HTTPException(403, "Access denied")
    
    # Get file stats
    stat = audio_file_path.stat()
    
    return {
        "job_id": job_id,
        "filename": f"audiobook_{job_id}.wav",
        "file_size": stat.st_size,
        "created_at": stat.st_ctime,
        "modified_at": stat.st_mtime,
        "download_url": f"/api/audio/{job_id}"
    }