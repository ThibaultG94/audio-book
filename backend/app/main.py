"""Main FastAPI application."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import configuration
try:
    from app.config import settings
except ImportError:
    from app.core.config import settings

# Import services with error handling
try:
    from app.core.startup_checks import StartupValidator
    startup_validator_available = True
except ImportError as e:
    logger.warning(f"StartupValidator not available: {e}")
    startup_validator_available = False

try:
    from app.services.splitter import BookSplitter
    book_splitter_available = True
except ImportError as e:
    logger.warning(f"BookSplitter not available: {e}")
    book_splitter_available = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Audio Book Converter API...")
    
    # Run startup checks if available
    if startup_validator_available:
        try:
            validator = StartupValidator()
            results = validator.validate_all()
            validator.print_startup_summary(results)
        except Exception as e:
            logger.error(f"Startup validation error: {e}")
    
    # Log configuration
    logger.info(f"Storage directory: {settings.storage_dir}")
    logger.info(f"Voices directory: {settings.voices_dir}")
    logger.info(f"Max file size: {settings.max_file_size / 1024 / 1024:.1f} MB")
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down Audio Book Converter API...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "status": "online"
    }


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint."""
    checks = {
        "api": "healthy",
        "storage": settings.storage_dir.exists(),
        "voices": settings.voices_dir.exists()
    }
    
    # Check if any voice models exist
    if settings.voices_dir.exists():
        voice_files = list(settings.voices_dir.glob("**/*.onnx"))
        checks["voice_models"] = len(voice_files)
    else:
        checks["voice_models"] = 0
    
    return {
        "status": "healthy" if all(v for k, v in checks.items() if k != "voice_models") else "degraded",
        "checks": checks
    }


# API info endpoint
@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "endpoints": {
            "health": "/health",
            "upload": "/api/upload",
            "convert": "/api/convert",
            "download": "/api/download/{file_id}",
            "voices": "/api/voices"
        }
    }


# Voices endpoint (basic)
@app.get("/api/voices")
async def list_voices():
    """List available TTS voices."""
    voices = []
    
    if settings.voices_dir.exists():
        for voice_file in settings.voices_dir.glob("**/*.onnx"):
            voice_name = voice_file.stem
            config_file = voice_file.with_suffix(".onnx.json")
            
            voices.append({
                "id": voice_name,
                "name": voice_name.replace("_", " ").title(),
                "model": str(voice_file.relative_to(settings.voices_dir)),
                "has_config": config_file.exists()
            })
    
    return {
        "count": len(voices),
        "voices": voices
    }


# Upload endpoint (placeholder)
@app.post("/api/upload")
async def upload_file():
    """File upload endpoint (placeholder)."""
    return {
        "message": "Upload endpoint - implementation pending",
        "max_size": settings.max_file_size,
        "allowed_extensions": settings.allowed_extensions
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
