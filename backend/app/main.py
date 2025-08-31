"""
FastAPI main application with endpoints for book conversion
"""
import os
import json
import asyncio
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
import tempfile
import shutil

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, WebSocket
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from app.services.splitter import BookSplitter
from app.services.tts import TTSService, ConversionJob, ConversionStatus
from app.config import Settings

# Initialize settings
settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title="TTS Book Converter API",
    description="Convert books (PDF/EPUB) to audiobooks with AI voices",
    version="1.0.0"
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
book_splitter = BookSplitter(
    output_base_dir=settings.PROCESSING_DIR,
    max_chapter_duration_minutes=settings.MAX_CHAPTER_DURATION_MINUTES
)

tts_service = TTSService(
    model_path=settings.PIPER_MODEL_PATH,
    config_path=settings.PIPER_CONFIG_PATH,
    output_format=settings.OUTPUT_FORMAT,
    max_workers=settings.MAX_TTS_WORKERS
)

# WebSocket connections for real-time progress
websocket_connections: Dict[str, List[WebSocket]] = {}

# --- Pydantic Models ---

class BookUploadResponse(BaseModel):
    book_id: str
    book_title: str
    total_chapters: int
    chapters: List[Dict]
    estimated_duration_seconds: int
    message: str

class ConversionStartRequest(BaseModel):
    book_id: str
    voice_model: Optional[str] = "default"
    speed: Optional[float] = 1.0

class ConversionStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    current_chapter: Optional[str]
    chapters_completed: int
    total_chapters: int
    error: Optional[str]
    output_url: Optional[str]

class ChapterInfo(BaseModel):
    index: int
    title: str
    status: str
    audio_url: Optional[str]
    duration_seconds: Optional[int]

# --- API Endpoints ---

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TTS Book Converter",
        "version": "1.0.0"
    }

@app.post("/api/upload", response_model=BookUploadResponse)
async def upload_book(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    author: Optional[str] = None
):
    """
    Upload and analyze a book file (PDF or EPUB)
    """
    # Validate file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ['.pdf', '.epub']:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Only PDF and EPUB are supported."
        )
    
    # Save uploaded file temporarily
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir) / file.filename
    
    try:
        # Save file
        content = await file.read()
        temp_path.write_bytes(content)
        
        # Split book into chapters
        result = book_splitter.split_book(
            file_path=str(temp_path),
            file_type=file_ext[1:],  # Remove dot
            book_title=title,
            author=author
        )
        
        return BookUploadResponse(
            book_id=result.book_id,
            book_title=result.book_title,
            total_chapters=result.total_chapters,
            chapters=result.chapters,
            estimated_duration_seconds=result.estimated_total_duration_seconds,
            message=f"Book analyzed successfully. Found {result.total_chapters} chapters."
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process book: {str(e)}"
        )
    
    finally:
        # Cleanup temp file
        shutil.rmtree(temp_dir, ignore_errors=True)

@app.post("/api/convert/start")
async def start_conversion(
    request: ConversionStartRequest,
    background_tasks: BackgroundTasks
):
    """
    Start TTS conversion for a book
    """
    # Get book manifest
    manifest_info = book_splitter.get_split_info(request.book_id)
    
    if not manifest_info:
        raise HTTPException(
            status_code=404,
            detail=f"Book {request.book_id} not found. Please upload first."
        )
    
    # Start conversion in background
    manifest_path = Path(settings.PROCESSING_DIR) / request.book_id / "manifest.json"
    
    # Create conversion task
    background_tasks.add_task(
        run_conversion_with_progress,
        request.book_id,
        str(manifest_path)
    )
    
    return {
        "message": "Conversion started",
        "book_id": request.book_id,
        "job_id": f"{request.book_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }

async def run_conversion_with_progress(book_id: str, manifest_path: str):
    """
    Run conversion with WebSocket progress updates
    """
    async def progress_callback(job_id: str, progress_data: Dict):
        # Send progress to all connected WebSocket clients
        if job_id in websocket_connections:
            for ws in websocket_connections[job_id]:
                try:
                    await ws.send_json(progress_data)
                except:
                    # Remove dead connections
                    websocket_connections[job_id].remove(ws)
    
    await tts_service.convert_book(
        book_id=book_id,
        manifest_path=manifest_path,
        progress_callback=progress_callback
    )

@app.get("/api/convert/status/{job_id}", response_model=ConversionStatusResponse)
async def get_conversion_status(job_id: str):
    """
    Get current status of a conversion job
    """
    status = tts_service.get_job_status(job_id)
    
    if not status:
        # Try to find by book_id
        book_id = job_id.split('_')[0]
        manifest_info = book_splitter.get_split_info(book_id)
        
        if manifest_info:
            # Check if conversion completed
            completed_chapters = sum(
                1 for ch in manifest_info['chapters'] 
                if ch['status'] == 'completed'
            )
            
            return ConversionStatusResponse(
                job_id=job_id,
                status='completed' if completed_chapters == manifest_info['total_chapters'] else 'pending',
                progress=completed_chapters / manifest_info['total_chapters'],
                current_chapter=None,
                chapters_completed=completed_chapters,
                total_chapters=manifest_info['total_chapters'],
                error=None,
                output_url=f"/api/download/{book_id}/archive" if completed_chapters > 0 else None
            )
        
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    return ConversionStatusResponse(
        job_id=status['job_id'],
        status=status['status'],
        progress=status['chapters_completed'] / status['total_chapters'] if status['total_chapters'] > 0 else 0,
        current_chapter=status.get('current_chapter'),
        chapters_completed=status['chapters_completed'],
        total_chapters=status['total_chapters'],
        error=status.get('error'),
        output_url=f"/api/download/{status['book_id']}/archive" if status['output_zip'] else None
    )

@app.get("/api/chapters/{book_id}")
async def get_chapters(book_id: str) -> List[ChapterInfo]:
    """
    Get list of chapters for a book
    """
    manifest_info = book_splitter.get_split_info(book_id)
    
    if not manifest_info:
        raise HTTPException(
            status_code=404,
            detail=f"Book {book_id} not found"
        )
    
    chapters = []
    for ch in manifest_info['chapters']:
        chapters.append(ChapterInfo(
            index=ch['index'],
            title=ch['title'],
            status=ch['status'],
            audio_url=f"/api/download/{book_id}/chapter/{ch['index']}" if ch.get('audio_file') else None,
            duration_seconds=ch.get('estimated_duration_seconds')
        ))
    
    return chapters

@app.get("/api/download/{book_id}/chapter/{chapter_index}")
async def download_chapter(book_id: str, chapter_index: int):
    """
    Download a single chapter audio file
    """
    manifest_info = book_splitter.get_split_info(book_id)
    
    if not manifest_info:
        raise HTTPException(
            status_code=404,
            detail=f"Book {book_id} not found"
        )
    
    # Find chapter
    chapter = next(
        (ch for ch in manifest_info['chapters'] if ch['index'] == chapter_index),
        None
    )
    
    if not chapter or not chapter.get('audio_file'):
        raise HTTPException(
            status_code=404,
            detail=f"Chapter {chapter_index} audio not found"
        )
    
    audio_path = Path(chapter['audio_file'])
    if not audio_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Audio file not found: {audio_path}"
        )
    
    return FileResponse(
        path=audio_path,
        media_type='audio/mpeg' if audio_path.suffix == '.mp3' else 'audio/wav',
        filename=audio_path.name
    )

@app.get("/api/download/{book_id}/archive")
async def download_archive(book_id: str):
    """
    Download complete audiobook as ZIP archive
    """
    # Find archive file
    book_dir = Path(settings.PROCESSING_DIR) / book_id
    zip_files = list(book_dir.glob("*.zip"))
    
    if not zip_files:
        raise HTTPException(
            status_code=404,
            detail=f"Archive not found for book {book_id}"
        )
    
    zip_path = zip_files[0]  # Take first zip file
    
    return FileResponse(
        path=zip_path,
        media_type='application/zip',
        filename=zip_path.name
    )

@app.websocket("/ws/progress/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time progress updates
    """
    await websocket.accept()
    
    # Register connection
    if job_id not in websocket_connections:
        websocket_connections[job_id] = []
    websocket_connections[job_id].append(websocket)
    
    try:
        # Keep connection alive
        while True:
            # Wait for messages (ping/pong)
            data = await websocket.receive_text()
            
            # Check job status
            status = tts_service.get_job_status(job_id)
            if status:
                await websocket.send_json(status)
            
            # If job is complete, close connection
            if status and status['status'] in ['completed', 'failed', 'cancelled']:
                break
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    
    finally:
        # Cleanup connection
        if job_id in websocket_connections:
            websocket_connections[job_id].remove(websocket)
            if not websocket_connections[job_id]:
                del websocket_connections[job_id]

@app.delete("/api/books/{book_id}")
async def delete_book(book_id: str):
    """
    Delete a book and all associated files
    """
    success = book_splitter.cleanup_book(book_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Book {book_id} not found"
        )
    
    return {"message": f"Book {book_id} deleted successfully"}

# --- Run Server ---

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )