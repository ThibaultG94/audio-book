"""Pydantic models for API requests and responses."""

from enum import Enum
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ConversionStatus(str, Enum):
    """Status of a TTS conversion job."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileUploadResponse(BaseModel):
    """Response after file upload."""
    file_id: str
    filename: str
    file_size: int
    uploaded_at: datetime


class ConversionRequest(BaseModel):
    """Request to start TTS conversion."""
    file_id: str
    voice_model: Optional[str] = None
    length_scale: Optional[float] = Field(default=1.0, ge=0.5, le=2.0)
    noise_scale: Optional[float] = Field(default=0.667, ge=0.0, le=1.0)
    noise_w: Optional[float] = Field(default=0.8, ge=0.0, le=1.0)
    sentence_silence: Optional[float] = Field(default=0.35, ge=0.1, le=2.0)


class ConversionResponse(BaseModel):
    """Response after starting conversion."""
    job_id: str
    status: ConversionStatus
    created_at: datetime


class ConversionStatusResponse(BaseModel):
    """Current status of a conversion job."""
    job_id: str
    status: ConversionStatus
    progress_percent: Optional[int] = None
    error_message: Optional[str] = None
    audio_file_url: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
