"""Conversion API routes for audiobook generation."""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel, Field

from app.services.conversion_service import conversion_service
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/convert", tags=["conversion"])


class ConversionRequest(BaseModel):
    """Request model for starting conversion."""
    file_id: str = Field(..., description="ID of uploaded file")
    voice_model: str = Field(..., description="Path to voice model")
    length_scale: float = Field(1.0, ge=0.5, le=2.0, description="Speech speed")
    noise_scale: float = Field(0.667, ge=0.0, le=1.0, description="Expressiveness")
    noise_w: float = Field(0.8, ge=0.0, le=1.0, description="Phonetic variation")
    sentence_silence: float = Field(0.35, ge=0.0, le=2.0, description="Pause between sentences")
    output_format: str = Field("wav", pattern="^(wav|mp3)$", description="Output audio format")


class ConversionResponse(BaseModel):
    """Response model for conversion start."""
    job_id: str
    status: str
    message: str


class ConversionStatusResponse(BaseModel):
    """Response model for conversion status."""
    job_id: str
    status: str
    progress: int
    started_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None
    steps: Dict[str, Any]
    output_file: Optional[str] = None
    duration_estimate: Optional[float] = None
    chapters: List[Dict[str, Any]]


@router.post("/start", response_model=ConversionResponse)
async def start_conversion(request: ConversionRequest):
    """Start a new audiobook conversion job.
    
    Args:
        request: Conversion parameters including file ID and voice settings
        
    Returns:
        ConversionResponse with job ID and initial status
    """
    try:
        # Validate uploaded file exists
        file_path = settings.UPLOAD_DIR / f"{request.file_id}"
        if not file_path.exists():
            # Check with common extensions
            for ext in ['.pdf', '.epub']:
                test_path = settings.UPLOAD_DIR / f"{request.file_id}{ext}"
                if test_path.exists():
                    file_path = test_path
                    break
            else:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Uploaded file not found: {request.file_id}"
                )
        
        # Validate voice model exists
        if not Path(request.voice_model).exists():
            # Check in voices directory
            voice_path = settings.VOICES_BASE_PATH / request.voice_model
            if not voice_path.exists():
                raise HTTPException(
                    status_code=400, 
                    detail=f"Voice model not found: {request.voice_model}"
                )
            request.voice_model = str(voice_path)
        
        # Prepare TTS parameters
        tts_params = {
            "length_scale": request.length_scale,
            "noise_scale": request.noise_scale,
            "noise_w": request.noise_w,
            "sentence_silence": request.sentence_silence
        }
        
        # Start conversion job
        job_id = await conversion_service.start_conversion(
            file_path=file_path,
            voice_model=request.voice_model,
            tts_params=tts_params,
            output_format=request.output_format
        )
        
        logger.info(f"Started conversion job: {job_id}")
        
        return ConversionResponse(
            job_id=job_id,
            status="started",
            message="Conversion started successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start conversion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=ConversionStatusResponse)
async def get_conversion_status(job_id: str):
    """Get current status of a conversion job.
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        ConversionStatusResponse with current progress and details
    """
    status = conversion_service.get_conversion_status(job_id)
    
    if not status:
        raise HTTPException(
            status_code=404, 
            detail=f"Conversion job not found: {job_id}"
        )
    
    return ConversionStatusResponse(**status)


@router.post("/cancel/{job_id}")
async def cancel_conversion(job_id: str):
    """Cancel an ongoing conversion job.
    
    Args:
        job_id: Job identifier to cancel
        
    Returns:
        Confirmation message
    """
    success = await conversion_service.cancel_conversion(job_id)
    
    if not success:
        raise HTTPException(
            status_code=404, 
            detail=f"Conversion job not found: {job_id}"
        )
    
    return {
        "message": "Conversion cancelled successfully",
        "job_id": job_id
    }


@router.delete("/{job_id}")
async def delete_conversion(job_id: str):
    """Delete a conversion job and its associated files.
    
    Args:
        job_id: Job identifier to delete
        
    Returns:
        Deletion confirmation
    """
    status = conversion_service.get_conversion_status(job_id)
    
    if not status:
        raise HTTPException(
            status_code=404, 
            detail=f"Conversion job not found: {job_id}"
        )
    
    # Delete output file if exists
    if status.get("output_file"):
        output_path = Path(status["output_file"])
        if output_path.exists():
            try:
                output_path.unlink()
                logger.info(f"Deleted output file: {output_path}")
            except Exception as e:
                logger.error(f"Failed to delete output file: {e}")
    
    # Remove from conversion tracking
    if job_id in conversion_service.conversions:
        del conversion_service.conversions[job_id]
    
    return {
        "message": "Conversion deleted successfully",
        "job_id": job_id
    }


@router.get("/list")
async def list_conversions(
    status_filter: Optional[str] = None,
    limit: int = 100
):
    """List all conversion jobs with optional filtering.
    
    Args:
        status_filter: Filter by status (completed, processing, failed)
        limit: Maximum number of results
        
    Returns:
        List of conversion jobs
    """
    conversions = conversion_service.list_conversions()
    
    # Apply status filter if provided
    if status_filter:
        conversions = [
            c for c in conversions 
            if c.get("status") == status_filter
        ]
    
    # Apply limit
    conversions = conversions[:limit]
    
    return {
        "conversions": conversions,
        "count": len(conversions),
        "total": len(conversion_service.conversions)
    }


@router.post("/retry/{job_id}")
async def retry_conversion(job_id: str):
    """Retry a failed conversion job.
    
    Args:
        job_id: Job identifier to retry
        
    Returns:
        New job ID for the retry attempt
    """
    # Get original job details
    original_status = conversion_service.get_conversion_status(job_id)
    
    if not original_status:
        raise HTTPException(
            status_code=404,
            detail=f"Original conversion job not found: {job_id}"
        )
    
    if original_status.get("status") != "failed":
        raise HTTPException(
            status_code=400,
            detail="Can only retry failed conversions"
        )
    
    # Extract original parameters
    file_path = Path(original_status.get("file_path"))
    voice_model = original_status.get("voice_model")
    output_format = original_status.get("output_format", "wav")
    
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Original file no longer exists"
        )
    
    # Start new conversion with same parameters
    new_job_id = await conversion_service.start_conversion(
        file_path=file_path,
        voice_model=voice_model,
        output_format=output_format
    )
    
    logger.info(f"Retrying conversion {job_id} as new job {new_job_id}")
    
    return {
        "original_job_id": job_id,
        "new_job_id": new_job_id,
        "status": "started",
        "message": "Conversion retry started successfully"
    }


@router.get("/stats")
async def get_conversion_stats():
    """Get statistics about all conversions.
    
    Returns:
        Statistics including counts by status and performance metrics
    """
    conversions = conversion_service.list_conversions()
    
    # Calculate statistics
    stats = {
        "total": len(conversions),
        "by_status": {},
        "average_duration": 0,
        "total_audio_generated": 0
    }
    
    # Count by status
    for conv in conversions:
        status = conv.get("status", "unknown")
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        
        # Add duration if available
        if conv.get("duration_estimate"):
            stats["total_audio_generated"] += conv["duration_estimate"]
    
    # Calculate average duration for completed conversions
    completed = [c for c in conversions if c.get("status") == "completed"]
    if completed:
        total_duration = sum(c.get("duration_estimate", 0) for c in completed)
        stats["average_duration"] = total_duration / len(completed)
    
    return stats


# Health check endpoint for this router
@router.get("/health")
async def conversion_health():
    """Check if conversion service is healthy.
    
    Returns:
        Health status of conversion service
    """
    return {
        "service": "conversion",
        "status": "healthy",
        "active_jobs": len([
            c for c in conversion_service.conversions.values()
            if c.get("status") in ["processing", "synthesizing", "extracting"]
        ]),
        "total_jobs": len(conversion_service.conversions)
    }