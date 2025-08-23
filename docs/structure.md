# 📁 Complete Audio Book Converter Project Structure

## Architecture Overview

```
audio-book/                               # 🏠 Project root directory
├── backend/                              # 🐍 Python FastAPI backend
│   ├── app/                              # Main application package
│   │   ├── __init__.py                   # App init (version, metadata)
│   │   ├── main.py                       # FastAPI application entry point
│   │   ├── api/                          # REST API layer
│   │   │   ├── __init__.py               # API package init
│   │   │   └── routes/                   # HTTP endpoints
│   │   │       ├── __init__.py           # Routes exports
│   │   │       ├── upload.py             # PDF/EPUB file upload endpoints
│   │   │       ├── convert.py            # TTS conversion with background jobs
│   │   │       ├── audio.py              # Generated audio file serving
│   │   │       └── preview.py            # 🆕 TTS preview for voice testing
│   │   ├── services/                     # Business logic layer
│   │   │   ├── __init__.py               # Services exports
│   │   │   ├── text_extractor.py         # PDF/EPUB → text extraction
│   │   │   ├── text_processor.py         # Text cleaning + chunking
│   │   │   ├── tts_engine.py             # Piper TTS interface
│   │   │   ├── audio_processor.py        # WAV concatenation
│   │   │   └── preview_tts.py            # 🆕 Lightweight TTS for previews
│   │   ├── models/                       # Pydantic schemas
│   │   │   ├── __init__.py               # Models exports
│   │   │   └── schemas.py                # Request/Response models
│   │   ├── core/                         # System configuration
│   │   │   ├── __init__.py               # Core exports
│   │   │   ├── config.py                 # Pydantic settings
│   │   │   ├── exceptions.py             # Custom exceptions
│   │   │   └── startup_checks.py         # 🆕 System validation on startup
│   │   └── utils/                        # General utilities
│   │       └── __init__.py
│   ├── tests/                            # Unit and integration tests
│   │   ├── __init__.py
│   │   ├── unit/                         # Service unit tests
│   │   │   ├── test_text_extractor.py
│   │   │   ├── test_text_processor.py
│   │   │   └── test_audio_routes.py
│   │   └── integration/                  # End-to-end tests
│   ├── voices/                           # Piper TTS voice models
│   │   └── fr/fr_FR/siwis/low/          # French voice example
│   │       ├── fr_FR-siwis-low.onnx     # ONNX neural model
│   │       └── fr_FR-siwis-low.onnx.json # Voice metadata
│   ├── storage/                          # Runtime file storage
│   │   ├── uploads/                      # Uploaded PDF/EPUB files
│   │   ├── outputs/                      # Generated WAV audio files
│   │   └── previews/                     # 🆕 Temporary preview audio files
│   ├── venv/                             # Python virtual environment
│   ├── requirements.txt                  # Production dependencies
│   └── requirements-dev.txt              # Development dependencies
│
├── frontend/                             # ⚛️  Next.js 15 frontend
│   ├── src/                              # TypeScript source code
│   │   ├── app/                          # Next.js App Router 13+
│   │   │   ├── layout.tsx                # Root layout (fonts, metadata)
│   │   │   ├── page.tsx                  # 🏠 Homepage with upload interface
│   │   │   ├── globals.css               # Global TailwindCSS styles
│   │   │   └── convert/[id]/             # Dynamic conversion pages
│   │   │       └── page.tsx              # Conversion status + progress
│   │   ├── components/                   # Reusable React components
│   │   │   ├── FileUpload.tsx            # Drag&drop upload with validation
│   │   │   ├── ConversionStatus.tsx      # Status polling + progress bar
│   │   │   └── VoicePreview.tsx          # 🆕 Voice testing + parameters
│   │   ├── lib/                          # Utilities and API client
│   │   │   ├── api.ts                    # HTTP client for backend API
│   │   │   └── types.ts                  # Shared TypeScript interfaces
│   │   └── __tests__/                    # Frontend Jest tests
│   │       └── components/
│   │           └── FileUpload.test.tsx   # Upload component tests
│   ├── public/                           # Static assets
│   ├── node_modules/                     # Node.js dependencies
│   ├── package.json                      # npm configuration + scripts
│   ├── tsconfig.json                     # TypeScript configuration
│   ├── next.config.ts                    # Next.js configuration
│   ├── tailwind.config.js               # TailwindCSS configuration
│   ├── postcss.config.mjs               # PostCSS configuration
│   ├── eslint.config.mjs                # ESLint configuration
│   ├── jest.config.js                    # Jest test configuration
│   ├── jest.setup.js                     # Test setup + mocks
│   └── .gitignore                        # Frontend-specific Git ignores
│
├── scripts/                              # 🛠️ DevOps automation scripts
│   ├── setup.sh                          # 🚀 Complete initial setup
│   ├── dev.sh                            # 🔥 Development environment startup
│   ├── backend.sh                        # 🐍 Backend only startup
│   ├── frontend.sh                       # ⚛️  Frontend only startup
│   ├── install-piper.sh                  # 🆕 Automatic Piper TTS installation
│   ├── fix-imports.sh                    # 🔧 Fix Python import issues
│   ├── build.sh                          # 🏗️ Production build
│   ├── test.sh                           # 🧪 Comprehensive testing
│   └── clean.sh                          # 🧹 Clean build artifacts
│
├── docs/                                 # 📚 Project documentation
│   └── structure.md                      # 📋 This file (detailed structure)
│
├── docker/                               # 🐳 Docker configuration (future)
│   ├── Dockerfile                        # Production multi-stage image
│   └── docker-compose.dev.yml           # Development with services
│
├── voices/                               # 🎵 Legacy voice models (compatibility)
│   └── fr/fr_FR/siwis/low/              # Same structure as backend/voices/
│
├── venv/                                 # 🐍 Legacy virtual environment
├── tts.py                                # 📜 Original CLI script (legacy)
├── .env                                  # 🔐 Local environment variables
├── .env.example                          # 📝 Environment variables template  
├── .gitignore                            # 🚫 Global Git ignore rules
├── Makefile                              # ⚡ Quick development commands
├── captain-definition                    # 🚢 CapRover deployment config
└── README.md                             # 📖 Main user documentation
```

## 🔧 Critical Components Details

### Backend - Modular Structure

#### `app/main.py` - FastAPI Entry Point
- Application initialization with CORS configuration
- Route inclusion (/upload, /convert, /audio, /preview)
- Error handling middleware
- Startup validation (Piper TTS, voice models)

#### `app/api/routes/` - REST Endpoints
- **upload.py**: POST /api/upload/file (multipart/form-data)
- **convert.py**: POST /api/convert/start + GET /api/convert/status/{job_id}
- **audio.py**: GET /api/audio/{job_id} (FileResponse streaming)
- **preview.py**: POST /api/preview/tts + GET /api/preview/audio/{preview_id}

#### `app/services/` - Decoupled Business Logic
- **text_extractor.py**: PyPDF2 + ebooklib + BeautifulSoup integration
- **text_processor.py**: Unicode normalization + paragraph chunking
- **tts_engine.py**: Subprocess interface to Piper CLI
- **audio_processor.py**: WAV concatenation with pauses
- **preview_tts.py**: Optimized TTS for short text samples

#### `app/core/` - Centralized Configuration
- **config.py**: Pydantic Settings with type validation
- **exceptions.py**: Custom exception hierarchy (TTSError, etc.)
- **startup_checks.py**: Piper TTS + voice models + directory validation

### Frontend - Modern Next.js Architecture

#### App Router (Next.js 13+)
- **layout.tsx**: Global configuration (Geist fonts, TailwindCSS)
- **page.tsx**: Homepage with FileUpload + VoicePreview components
- **convert/[id]/page.tsx**: Real-time status with polling

#### Reusable Components
- **FileUpload.tsx**: react-dropzone + validation + upload progress
- **ConversionStatus.tsx**: API polling + progress bar + download link
- **VoicePreview.tsx**: Textarea + TTS test + audio player + settings

#### API Layer
- **api.ts**: HTTP client with error handling + retry logic + types
- **types.ts**: Shared interfaces between backend/frontend

### Automation Scripts

#### Development Workflow
- **setup.sh**: Virtual env creation + npm install + Piper TTS + directories
- **dev.sh**: Concurrent backend + frontend startup with cleanup
- **install-piper.sh**: OS detection + automatic Piper binary download

#### Quality Assurance
- **test.sh**: pytest backend + jest frontend (if configured)
- **fix-imports.sh**: Python import resolution + __init__.py creation
- **clean.sh**: Build artifacts cleanup + optional storage cleanup

### Configuration and Deployment

#### Environment Variables (.env)
```bash
# Application
DEBUG=false
APP_NAME="TTS Audio Book Converter"

# TTS Configuration
VOICE_MODEL=voices/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx
LENGTH_SCALE=1.0              # Speech speed
NOISE_SCALE=0.667             # Voice variation
SENTENCE_SILENCE=0.35         # Pause between sentences
PAUSE_BETWEEN_BLOCKS=0.35     # Pause between blocks

# File Limits
MAX_FILE_SIZE=52428800        # 50MB
MAX_CHUNK_CHARS=1500          # Text chunk size

# URLs
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### CapRover (captain-definition)
```json
{
  "schemaVersion": 2,
  "dockerfilePath": "./Dockerfile"
}
```

## 🚀 Data Flow and Architecture

### Complete User Workflow

1. **Homepage** (`app/page.tsx`)
   - VoicePreview component → test voice with custom parameters
   - FileUpload component → upload PDF/EPUB

2. **File Upload** (`api/routes/upload.py`)
   - Extension + size validation
   - Storage in `storage/uploads/`
   - Return unique `file_id`

3. **Conversion Start** (`api/routes/convert.py`)
   - Text extraction (`text_extractor.py`)
   - Cleaning + chunking (`text_processor.py`)
   - TTS synthesis by blocks (`tts_engine.py`)
   - Audio concatenation (`audio_processor.py`)
   - Async job with status polling

4. **Real-time Status** (`convert/[id]/page.tsx`)
   - Polling GET `/api/convert/status/{job_id}`
   - Progress bar display
   - Download link when completed

5. **Audio Download** (`api/routes/audio.py`)
   - FileResponse streaming
   - Appropriate headers (Content-Disposition)

### Voice Preview Workflow (New)

1. **Preview Interface** (`components/VoicePreview.tsx`)
   - Customizable text textarea (max 500 chars)
   - Voice parameter sliders (speed, variation)
   - Available voice selection

2. **Preview Generation** (`api/routes/preview.py`)
   - POST `/api/preview/tts` with short text
   - Fast processing (`preview_tts.py`)
   - Temporary storage `storage/previews/`

3. **Audio Playback** 
   - GET `/api/preview/audio/{preview_id}`
   - Integrated HTML5 player
   - Download option for preview

## 📊 Technologies and Dependencies

### Backend Python Stack
```txt
# Core framework
fastapi==0.104.1              # Modern REST API framework
uvicorn[standard]==0.24.0     # ASGI server

# Configuration  
pydantic-settings==2.1.0      # Settings with validation

# Text processing
PyPDF2==3.0.1                 # PDF text extraction
ebooklib==0.18                # EPUB text extraction  
beautifulsoup4==4.12.2        # HTML parsing
lxml==4.9.3                   # Fast XML parser

# Development tools
pytest==7.4.3                 # Testing framework
ruff==0.1.6                   # Linting + formatting
mypy==1.7.1                   # Type checking
```

### Frontend Node.js Stack
```json
{
  "dependencies": {
    "next": "15.5.0",           // React SSR framework
    "react": "19.1.0",          // User interface library  
    "react-dom": "19.1.0",      // React DOM integration
    "react-dropzone": "^14.3.8", // Drag&drop file upload
    "lucide-react": "^0.540.0"  // Modern icon library
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4", // Utility-first CSS
    "typescript": "^5",          // Static typing
    "eslint": "^9",             // JavaScript linting
    "jest": "^29.7.0"           // Unit testing framework
  }
}
```

### External System Dependencies
- **Piper TTS**: System binary for neural voice synthesis
- **Voice Models**: ONNX + JSON files (neural networks)
- **Docker**: Production containerization (optional)

## 🔄 Migration and Evolution

### Legacy Files Maintained
- `tts.py`: Original CLI script (still functional)
- `voices/`: Old voice models location
- `venv/`: Legacy virtual environment at root

### Architectural Improvements v1 → v2
- ✅ Monorepo with separated backend/frontend
- ✅ Decoupled REST API with FastAPI
- ✅ Modern Next.js + TypeScript interface
- ✅ Development automation scripts
- ✅ Structured testing approach
- ✅ Centralized configuration
- 🆕 Integrated voice preview system
- 🆕 Robust startup validation
- 🔜 Multi-voice support
- 🔜 Redis job queue (optional)
- 🔜 User authentication
- 🔜 Conversion history

## 🚀 Available Commands and Scripts

### Makefile Quick Commands
```bash
make setup      # Complete initial installation
make dev        # Development (backend + frontend)
make backend    # Backend only (FastAPI)
make frontend   # Frontend only (Next.js)
make test       # Comprehensive testing
make build      # Production build
make clean      # Clean build artifacts
make help       # Show available commands
```

### Detailed Script Functions

#### `scripts/setup.sh` - Initial Installation
- Python virtual environment creation
- Backend + frontend dependency installation  
- Automatic Piper TTS detection and installation
- Storage directory creation
- .env file generation
- System validation

#### `scripts/dev.sh` - Development Environment
- Concurrent backend (port 8000) + frontend (port 3000) startup
- Auto-reload on file changes
- Process cleanup management (Ctrl+C)
- Real-time log display

#### `scripts/install-piper.sh` - Piper TTS Installation
- Automatic OS/architecture detection
- Appropriate GitHub release download
- System installation (/usr/local/bin)
- Post-installation validation tests

#### `scripts/fix-imports.sh` - Python Issues Resolution
- Missing directory creation
- __init__.py file generation
- Application import testing
- Modular structure validation

## 🧪 Testing and Validation

### Test Structure
```
backend/tests/
├── __init__.py
├── conftest.py                       # Shared pytest fixtures
├── unit/                             # Service unit tests
│   ├── test_text_extractor.py        # PDF/EPUB extraction tests
│   ├── test_text_processor.py        # Text cleaning tests
│   ├── test_tts_engine.py            # Piper interface tests
│   └── test_audio_routes.py          # Audio endpoint tests
└── integration/                      # End-to-end tests
    └── test_full_workflow.py         # Complete upload→conversion

frontend/src/__tests__/
├── components/
│   ├── FileUpload.test.tsx           # Upload component tests
│   ├── ConversionStatus.test.tsx     # Status polling tests  
│   └── VoicePreview.test.tsx         # Voice preview tests
└── lib/
    └── api.test.ts                   # API client tests
```

### Test Commands
```bash
# Backend only
cd backend && source venv/bin/activate
python -m pytest tests/ -v
python -m pytest tests/ --cov=app --cov-report=html

# Frontend only  
cd frontend && npm test
npm test -- --watch --coverage

# Complete testing
make test  # or ./scripts/test.sh
```

## 🐳 Docker and Deployment

### Production Docker Structure
```
docker/
├── Dockerfile                        # Multi-stage production build
├── Dockerfile.dev                    # Development image
├── docker-compose.prod.yml           # Production with services
└── docker-compose.dev.yml            # Local development
```

### Multi-stage Dockerfile Example
```dockerfile
# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production
COPY frontend/ .
RUN npm run build

# Stage 2: Python backend + frontend static files
FROM python:3.11-slim AS production
RUN apt-get update && apt-get install -y \
    wget curl && \
    rm -rf /var/lib/apt/lists/*

# Install Piper TTS
RUN wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz && \
    tar -xzf piper_amd64.tar.gz && \
    mv piper/piper /usr/local/bin/ && \
    rm -rf piper*

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY --from=frontend-builder /app/frontend/out ./frontend/out
COPY voices/ ./voices/

EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### CapRover Deployment Configuration
```json
{
  "schemaVersion": 2,
  "dockerfilePath": "./docker/Dockerfile",
  "context": ".",
  "containerHttpPort": "8000"
}
```

## 🔐 Security and Best Practices

### User Input Validation
- File size limits (50MB MAX_FILE_SIZE)
- Extension validation (.pdf, .epub only)
- Filename sanitization (UUID + extension)
- Preview text limits (500 chars max)
- TTS parameter validation (defined ranges)

### Isolation and Sandboxing
- Subprocess TTS processing with timeouts
- File storage in dedicated directories
- Path traversal protection (relative_to checks)
- Automatic temporary file cleanup

### Environment Variable Security
```bash
# Never commit sensitive variables
DATABASE_URL=postgresql://...
SECRET_KEY=super-secret-key
OPENAI_API_KEY=sk-...

# Public variables are safe
NEXT_PUBLIC_API_URL=https://api.domain.com
VOICE_MODEL=voices/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx
```

## 🔧 Advanced Configuration

### Pydantic Settings (app/core/config.py)
```python
class Settings(BaseSettings):
    # Application
    app_name: str = "TTS Audio Book Converter"
    debug: bool = False
    
    # Paths  
    voices_dir: Path = Path("voices")
    storage_dir: Path = Path("storage")
    uploads_dir: Path = Path("storage/uploads")
    outputs_dir: Path = Path("storage/outputs")
    
    # TTS Engine
    voice_model: str = "voices/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx"
    length_scale: float = 1.0
    noise_scale: float = 0.667
    noise_w: float = 0.8
    sentence_silence: float = 0.35
    pause_between_blocks: float = 0.35
    
    # Processing  
    max_chunk_chars: int = 1500
    max_file_size: int = 50 * 1024 * 1024
    allowed_extensions: set[str] = {".pdf", ".epub"}
    
    class Config:
        env_file = ".env"
```

### Next.js Configuration (next.config.ts)
```typescript
const nextConfig: NextConfig = {
  output: 'export',                    // Static export for CapRover
  trailingSlash: true,                // Server compatibility
  images: { unoptimized: true },      // No image optimization
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`
      }
    ]
  }
}
```

## 📈 Monitoring and Observability

### Structured Logging
```python
import structlog

logger = structlog.get_logger()

# In services
logger.info("conversion_started", 
           file_id=file_id, 
           job_id=job_id,
           voice_model=voice_model)

logger.error("tts_generation_failed",
            error=str(e),
            text_length=len(text),
            voice_model=voice_model)
```

### Application Metrics
```python
# Example metrics to track
- conversion_duration_seconds
- file_upload_size_bytes  
- tts_generation_errors_total
- voice_preview_requests_total
- concurrent_conversions_gauge
```

### Health Checks
```python
# backend/app/main.py
@app.get("/health")
async def health_check():
    checks = StartupValidator.validate_all()
    status = "healthy" if all(checks.values()) else "unhealthy"
    return {
        "status": status,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

This modular structure ensures a robust, maintainable, and deployable application with all modern development best practices.