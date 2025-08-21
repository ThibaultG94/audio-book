"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import upload, convert, audio


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="1.0.0"
    )
    
    # CORS middleware for frontend integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # Next.js dev server
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
    app.include_router(convert.router, prefix="/api/convert", tags=["convert"])
    app.include_router(audio.router, prefix="/api/audio", tags=["audio"])
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {"message": "TTS Audio Book Converter API", "version": "1.0.0"}
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )