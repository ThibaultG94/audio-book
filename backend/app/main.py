"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.api.routes import upload, convert, audio, preview  # Add preview

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    settings = get_settings()
    
    # Create necessary directories
    for directory in [settings.UPLOAD_DIR, settings.OUTPUT_DIR, settings.TEMP_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")
    
    # Verify Piper installation
    try:
        from app.services.tts_engine import TTSEngine
        tts_engine = TTSEngine()
        logger.info("TTS Engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize TTS Engine: {e}")
        logger.warning("Application will start but TTS features may not work")
    
    # Verify voices directory
    if not settings.VOICES_BASE_PATH.exists():
        logger.warning(f"Voices directory not found: {settings.VOICES_BASE_PATH}")
        logger.warning("Please download voice models for TTS functionality")
    else:
        # Count available voices
        voice_files = list(settings.VOICES_BASE_PATH.rglob("*.onnx"))
        logger.info(f"Found {len(voice_files)} voice model files")
    
    yield
    
    # Cleanup on shutdown
    logger.info("Application shutting down")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="Convert PDF and EPUB documents to high-quality audiobooks using AI TTS",
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(preview.router)  # Add preview routes
    app.include_router(upload.router)
    app.include_router(convert.router)
    app.include_router(audio.router)
    
    # Serve static files (for audio downloads)
    if settings.OUTPUT_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(settings.OUTPUT_DIR)), name="static")
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Audio Book Converter API",
            "version": settings.VERSION,
            "docs": "/docs"
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "voices_available": settings.VOICES_BASE_PATH.exists()
        }
    
    return app


# Create app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )