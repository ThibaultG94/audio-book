"""FastAPI application entry point."""

import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.exceptions import add_exception_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create FastAPI application instance."""
    settings = get_settings()
    
    # Initialize FastAPI app
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Create required directories
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Add exception handlers
    add_exception_handlers(app)
    
    # Mount static files (for serving audio files)
    if settings.OUTPUT_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(settings.OUTPUT_DIR)), name="static")
    
    # Include API routes
    from app.api.routes import upload, convert, audio, voice, preview
    
    app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
    app.include_router(convert.router, prefix="/api/convert", tags=["convert"])
    app.include_router(audio.router, prefix="/api/audio", tags=["audio"])
    app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
    app.include_router(preview.router, prefix="/api/preview", tags=["preview"])
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.VERSION
        }
    
    logger.info(f"✅ FastAPI app created - {settings.APP_NAME} v{settings.VERSION}")
    return app


# Create app instance
app = create_app()