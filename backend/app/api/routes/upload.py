from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid
import shutil
from datetime import datetime

from app.core.config import settings
from app.models.schemas import FileUploadResponse

router = APIRouter()

@router.post("/file", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload PDF or EPUB file for conversion."""
    
    # Validate file extension
    file_suffix = Path(file.filename).suffix.lower()
    if file_suffix not in settings.allowed_extensions:
        raise HTTPException(400, f"Unsupported file type: {file_suffix}")
    
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    file_path = settings.uploads_dir / f"{file_id}{file_suffix}"
    
    # Ensure upload directory exists
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(500, f"Failed to save file: {str(e)}")
    
    return FileUploadResponse(
        file_id=file_id,
        filename=file.filename,
        file_size=file_path.stat().st_size,
        uploaded_at=datetime.now()
    )
