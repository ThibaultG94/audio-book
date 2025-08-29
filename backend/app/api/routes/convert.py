from fastapi import APIRouter, HTTPException, BackgroundTasks
import asyncio
from pathlib import Path
import uuid
import tempfile
from datetime import datetime

from app.models.schemas import (
    ConversionRequest, ConversionResponse, ConversionStatusResponse, 
    ConversionStatus
)
from app.services.text_extractor import TextExtractor
from app.services.text_processor import TextProcessor
from app.services.tts_engine import TTSEngine
from app.services.audio_processor import AudioProcessor
from app.core.config import settings

router = APIRouter()

# In-memory job storage (use Redis/DB in production)
conversion_jobs: dict[str, ConversionStatusResponse] = {}

async def process_conversion_job(job_id: str, file_path: Path, request: ConversionRequest):
    """Background task to process TTS conversion."""
    try:
        # Update status to processing
        conversion_jobs[job_id].status = ConversionStatus.PROCESSING
        conversion_jobs[job_id].progress_percent = 10
        
        # Extract text
        raw_text = TextExtractor.extract_from_file(file_path)
        conversion_jobs[job_id].progress_percent = 30
        
        # Clean and chunk text
        clean_text = TextProcessor.clean_text(raw_text)
        chunks = list(TextProcessor.chunk_paragraphs(clean_text))
        conversion_jobs[job_id].progress_percent = 40
        
        # Initialize TTS engine
        tts_engine = TTSEngine()
        
        # Resolve voice model path
        voice_model = request.voice_model or settings.DEFAULT_VOICE_MODEL
        voice_path = None
        
        # Search for voice model file
        voice_path = None
        
        # Try exact path first (relative to voices_dir)
        candidate_path = settings.voices_dir / voice_model
        if candidate_path.exists():
            voice_path = candidate_path
        else:
            # If voice_model starts with "voices/", try removing that prefix
            if voice_model.startswith("voices/"):
                candidate_path = settings.voices_dir / voice_model[7:]  # Remove "voices/" prefix
                if candidate_path.exists():
                    voice_path = candidate_path
            
            # If still not found, search recursively by filename
            if not voice_path:
                # Extract filename from path
                filename = Path(voice_model).name
                for candidate in settings.voices_dir.rglob(filename):
                    if candidate.suffix == ".onnx":
                        voice_path = candidate
                        break
        
        if not voice_path:
            raise Exception(f"Voice model not found: {voice_model}")
        
        # Generate audio for each chunk
        temp_wavs = []
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            
            for i, chunk in enumerate(chunks):
                chunk_wav = tmp_path / f"chunk_{i:05d}.wav"
                await tts_engine.synthesize_text(
                    text=chunk,
                    voice_path=str(voice_path),
                    output_path=str(chunk_wav),
                    length_scale=request.length_scale or settings.DEFAULT_LENGTH_SCALE,
                    noise_scale=request.noise_scale or settings.DEFAULT_NOISE_SCALE,
                    noise_w=request.noise_w or settings.DEFAULT_NOISE_W,
                    sentence_silence=request.sentence_silence or settings.DEFAULT_SENTENCE_SILENCE
                )
                temp_wavs.append(chunk_wav)
                
                # Update progress
                progress = 40 + (50 * (i + 1) / len(chunks))
                conversion_jobs[job_id].progress_percent = int(progress)
            
            # Concatenate all chunks
            output_path = settings.outputs_dir / f"{job_id}.wav"
            settings.outputs_dir.mkdir(parents=True, exist_ok=True)
            
            AudioProcessor.concatenate_wav_files(
                temp_wavs, 
                output_path,
                pause_between=settings.pause_between_blocks
            )
        
        # Mark as completed
        conversion_jobs[job_id].status = ConversionStatus.COMPLETED
        conversion_jobs[job_id].progress_percent = 100
        conversion_jobs[job_id].audio_file_url = f"/api/audio/{job_id}"
        conversion_jobs[job_id].completed_at = datetime.now()
        
    except Exception as e:
        conversion_jobs[job_id].status = ConversionStatus.FAILED
        conversion_jobs[job_id].error_message = str(e)

@router.post("/start", response_model=ConversionResponse)
async def start_conversion(request: ConversionRequest, background_tasks: BackgroundTasks):
    """Start TTS conversion for uploaded file."""
    
    # Find uploaded file
    file_path = None
    for ext in settings.allowed_extensions:
        candidate = settings.uploads_dir / f"{request.file_id}{ext}"
        if candidate.exists():
            file_path = candidate
            break
    
    if not file_path:
        raise HTTPException(404, "Uploaded file not found")
    
    # Create job
    job_id = str(uuid.uuid4())
    job_status = ConversionStatusResponse(
        job_id=job_id,
        status=ConversionStatus.PENDING,
        created_at=datetime.now()
    )
    conversion_jobs[job_id] = job_status
    
    # Start background processing (run async task)
    asyncio.create_task(process_conversion_job(job_id, file_path, request))
    
    return ConversionResponse(
        job_id=job_id,
        status=ConversionStatus.PENDING,
        created_at=datetime.now()
    )

@router.get("/status/{job_id}", response_model=ConversionStatusResponse)
async def get_conversion_status(job_id: str):
    """Get current status of conversion job."""
    if job_id not in conversion_jobs:
        raise HTTPException(404, "Job not found")
    
    return conversion_jobs[job_id]