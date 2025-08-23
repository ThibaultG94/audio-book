"""FastAPI application entry point with preview route included."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
# Import ALL routes including preview ⚠️ This was missing!
from app.api.routes import upload, convert, audio, preview


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        description="Convert PDF and EPUB to audio books with AI voice preview",
        version="1.0.0",
        debug=settings.debug,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "*" if settings.debug else "https://yourdomain.com"
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
        allow_headers=["*"],
    )
    
    # Include ALL routes - ⚠️ PREVIEW WAS MISSING HERE!
    app.include_router(upload.router, prefix="/api/upload", tags=["file-upload"])
    app.include_router(convert.router, prefix="/api/convert", tags=["conversion"]) 
    app.include_router(audio.router, prefix="/api/audio", tags=["audio"])
    app.include_router(preview.router, prefix="/api/preview", tags=["preview"])  # ⚠️ ADD THIS LINE!
    
    @app.get("/")
    async def root():
        return {
            "message": "TTS Audio Book Converter API",
            "version": "1.0.0",
            "features": ["upload", "convert", "audio", "preview"],
            "available_routes": [
                "/api/upload/file",
                "/api/convert/start",
                "/api/convert/status/{job_id}",
                "/api/audio/{job_id}",
                "/api/preview/tts",  # ⚠️ THIS SHOULD BE LISTED
                "/api/preview/voices",
                "/api/preview/audio/{preview_id}"
            ]
        }
    
    @app.get("/health")
    async def health_check():
        """Health check with route verification."""
        # Get all registered routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                for method in route.methods:
                    if method != 'HEAD':  # Skip HEAD methods
                        routes.append(f"{method} {route.path}")
        
        return {
            "status": "healthy",
            "message": "Audio Book Converter API is running",
            "routes": sorted(routes),  # ⚠️ This will show if preview routes are registered
            "preview_available": "/api/preview/tts" in [route.path for route in app.routes if hasattr(route, 'path')]
        }
    
    # Debug endpoint to list all routes
    @app.get("/debug/routes")
    async def debug_routes():
        """Debug endpoint to see all registered routes."""
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append({
                    "path": route.path,
                    "methods": list(route.methods),
                    "name": getattr(route, 'name', 'unnamed')
                })
        return {"routes": routes}
    
    return app


# Create the FastAPI app instance
app = create_app()

# Development server entry point
if __name__ == "__main__":
    import uvicorn
    
    print("🔥 Starting development server...")
    print("📍 Available endpoints:")
    print("  • http://localhost:8000 - API info")
    print("  • http://localhost:8000/health - Health check")
    print("  • http://localhost:8000/docs - API documentation")
    print("  • http://localhost:8000/debug/routes - All routes")
    print("  • http://localhost:8000/api/preview/tts - Preview TTS")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )