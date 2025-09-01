"""Conversion API routes."""

import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel, Field

from app.services.conversion_service import conversion_service
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/convert", tags=["conversion"])


class ConversionRequest(BaseModel):
    """Request model for starting conversion."""
    file_id: str = Field(..., description="ID of uploaded file")
    voice_model: str = Field(..., description="Path to voice model")
    length_scale: float = Field(1.0, ge=0.5, le=2.0)
    noise_scale: float = Field(0.667, ge=0.0, le=1.0)
    noise_w: float = Field(0.8, ge=0.0, le=1.0)
    sentence_silence: float = Field(0.35, ge=0.0, le=2.0)
    output_format: str = Field("wav", pattern="^(wav|mp3)$")


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
    steps: dict
    output_file: Optional[str] = None
    duration_estimate: Optional[float] = None
    chapters: list


@router.get("/status/{job_id}", response_model=ConversionStatusResponse)
async def get_conversion_status(job_id: str):
    """Get status of a conversion job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        ConversionStatusResponse: Current job status
    """
    status = conversion_service.get_conversion_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Conversion job not found")
    
    return ConversionStatusResponse(**status)


@router.delete("/{job_id}")
async def delete_conversion(job_id: str):
    """Delete a conversion job and its associated files.
    
    Args:
        job_id: Job identifier
        
    Returns:
        dict: Deletion result
    """
    status = conversion_service.get_conversion_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Conversion job not found")
    
    # Delete output file if exists
    if status.get("output_file"):
        output_path = Path(status["output_file"])
        if output_path.exists():
            output_path.unlink()
    
    # Remove from conversions
    if job_id in conversion_service.conversions:
        del conversion_service.conversions[job_id]
    
    return {"message": "Conversion deleted successfully", "job_id": job_id}


@router.post("/cancel/{job_id}")
async def cancel_conversion(job_id: str):
    """Cancel an ongoing conversion job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        dict: Cancellation result
    """
    success = await conversion_service.cancel_conversion(job_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Conversion job not found")
    
    return {"message": "Conversion cancelled successfully", "job_id": job_id}


@router.get("/list")
async def list_conversions():
    """List all conversion jobs.
    
    Returns:
        dict: List of all conversions
    """
    conversions = conversion_service.list_conversions()
    return {
        "conversions": conversions,
        "count": len(conversions)
    }


@router.post("/start", response_model=ConversionResponse)
async def start_conversion(request: ConversionRequest):
    """Start a new audiobook conversion job.
    
    Args:
        request: Conversion parameters
        
    Returns:
        ConversionResponse: Job ID and initial status
    """
    try:
        # Validate file exists
        file_path = settings.UPLOAD_DIR / f"{request.file_id}"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Uploaded file not found")
        
        # Validate voice model
        if not Path(request.voice_model).exists():
            raise HTTPException(status_code=400, detail="Voice model not found")
        
        # Prepare TTS parameters
        tts_params = {
            "length_scale": request.length_scale,
            "noise_scale": request.noise_scale,
            "noise_w": request.noise_w,
            "sentence_silence": request.sentence_silence
        }
        
        # Start conversion
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
        
    except Exception as e:
        logger.error(f"Failed to start conversion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))