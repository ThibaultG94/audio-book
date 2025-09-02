"""File upload API routes."""

import logging
import shutil
from pathlib import Path
from typing import List
import uuid

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/upload", tags=["upload"])


class FileUploadResponse(BaseModel):
    """Response model for file upload."""
    file_id: str
    filename: str
    file_size: int
    content_type: str
    upload_path: str


@router.post("/file", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a PDF or EPUB file for conversion.
    
    Args:
        file: Uploaded file
        
    Returns:
        File upload response with file ID
    """
    try:
        # Validate file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > settings.MAX_FILE_SIZE:
            max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {max_size_mb}MB"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Save file
        upload_path = settings.UPLOAD_DIR / f"{file_id}{file_extension}"
        
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File uploaded: {file.filename} -> {upload_path}")
        
        return FileUploadResponse(
            file_id=file_id,
            filename=file.filename,
            file_size=file_size,
            content_type=file.content_type or "application/octet-stream",
            upload_path=str(upload_path)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_uploads():
    """List all uploaded files.
    
    Returns:
        List of uploaded files
    """
    try:
        uploads = []
        
        if not settings.UPLOAD_DIR.exists():
            return {"files": [], "count": 0}
        
        for file_path in settings.UPLOAD_DIR.iterdir():
            if file_path.is_file():
                uploads.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                })
        
        uploads.sort(key=lambda x: x["modified"], reverse=True)
        
        return {
            "files": uploads,
            "count": len(uploads)
        }
        
    except Exception as e:
        logger.error(f"Failed to list uploads: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{file_id}")
async def delete_upload(file_id: str):
    """Delete an uploaded file.
    
    Args:
        file_id: File identifier
        
    Returns:
        Confirmation message
    """
    try:
        # Try different extensions
        file_deleted = False
        for ext in settings.ALLOWED_EXTENSIONS:
            file_path = settings.UPLOAD_DIR / f"{file_id}{ext}"
            if file_path.exists():
                file_path.unlink()
                file_deleted = True
                logger.info(f"Deleted upload: {file_path}")
                break
        
        if not file_deleted:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {"message": f"File {file_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))