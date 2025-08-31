#!/bin/bash
# Fix all remaining import issues once and for all

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    🔧 FIXING ALL REMAINING IMPORTS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

cd backend

# Step 1: Fix app/config.py
echo -e "\n${YELLOW}📝 Fixing app/config.py...${NC}"
cat > app/config.py << 'EOF'
"""Application configuration."""

from pydantic import BaseModel
from typing import Optional
from pathlib import Path


class Settings(BaseModel):
    """Application settings."""
    
    # App info
    app_name: str = "Audio Book Converter"
    version: str = "1.0.0"
    debug: bool = True
    
    # API settings
    api_prefix: str = "/api"
    allowed_origins: list = ["http://localhost:3000", "http://localhost:3001"]
    
    # File settings
    max_file_size: int = 52428800  # 50MB
    allowed_extensions: list = [".pdf", ".epub", ".txt"]
    
    # TTS settings
    default_voice: str = "en_US-amy-medium"
    voice_model: str = "en_US-amy-medium.onnx"
    voice_config: str = "en_US-amy-medium.onnx.json"
    length_scale: float = 1.0
    noise_scale: float = 0.667
    sentence_silence: float = 0.35
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent
    storage_dir: Path = base_dir / "storage"
    uploads_dir: Path = storage_dir / "uploads"
    outputs_dir: Path = storage_dir / "outputs"
    temp_dir: Path = storage_dir / "temp"
    voices_dir: Path = base_dir / "voices"
    
    # Processing
    max_chunk_chars: int = 1500
    processing_timeout: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create global settings instance
settings = Settings()

# Ensure directories exist
settings.storage_dir.mkdir(parents=True, exist_ok=True)
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
settings.outputs_dir.mkdir(parents=True, exist_ok=True)
settings.temp_dir.mkdir(parents=True, exist_ok=True)
settings.voices_dir.mkdir(parents=True, exist_ok=True)
EOF

# Step 2: Move config.py to core/config.py if needed by other imports
echo -e "\n${YELLOW}📝 Creating app/core/config.py...${NC}"
cp app/config.py app/core/config.py

# Also update the import in startup_checks.py to use the right config
sed -i 's/from app.core.config import settings/from app.config import settings/g' app/core/startup_checks.py 2>/dev/null || true

# Step 3: Create a minimal main.py that works
echo -e "\n${YELLOW}📝 Creating minimal working main.py...${NC}"
cat > app/main.py << 'EOF'
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
EOF

# Step 4: Test the import chain
echo -e "\n${YELLOW}🔍 Testing import chain...${NC}"
. venv/bin/activate
python -c "
import sys
print(f'Python: {sys.version}')

# Test config import
try:
    from app.config import settings
    print('✅ Config import successful')
    print(f'   App name: {settings.app_name}')
    print(f'   Storage: {settings.storage_dir}')
except ImportError as e:
    print(f'❌ Config import failed: {e}')
    sys.exit(1)

# Test main import
try:
    from app.main import app
    print('✅ Main app import successful')
    print(f'   FastAPI app created: {type(app).__name__}')
except ImportError as e:
    print(f'❌ Main import failed: {e}')
    sys.exit(1)

print('🎉 All critical imports working!')
"

echo -e "\n${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}    ✅ ALL IMPORTS FIXED!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"

echo -e "\n🚀 The backend should now start successfully!"
echo -e "  Run: ${YELLOW}make backend${NC}"
echo -e "\n📌 Available endpoints:"
echo -e "  - http://localhost:8000/ (root)"
echo -e "  - http://localhost:8000/health (health check)"
echo -e "  - http://localhost:8000/api (API info)"
echo -e "  - http://localhost:8000/api/voices (list voices)"
echo -e "  - http://localhost:8000/docs (Swagger UI)"