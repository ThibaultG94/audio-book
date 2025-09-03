from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class Status(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ConversionRequest(BaseModel):
    file_id: str
    voice_model: str = "default"

class ConversionResponse(BaseModel):
    job_id: str
    status: str
    message: str

class ConversionStatusResponse(BaseModel):
    job_id: str              # LE CHAMP CRITIQUE
    status: Status
    progress: int = 0
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
