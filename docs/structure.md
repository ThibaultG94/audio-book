# 📁 Audio Book Converter - Project Structure

Modern text-to-speech application with FastAPI backend and Next.js frontend, featuring neural voice synthesis with Piper TTS.

## 🏗️ Complete Architecture Overview

```
audio-book/                               # 🏠 Project root directory
├── backend/                              # 🐍 Python FastAPI backend (port 8001)
│   ├── app/                              # Main application package
│   │   ├── main.py                       # FastAPI application entry point
│   │   ├── api/routes/                   # REST API endpoints
│   │   │   ├── voice.py                  # Voice management & discovery
│   │   │   ├── preview.py                # Real-time TTS previews
│   │   │   ├── upload.py                 # PDF/EPUB file upload
│   │   │   ├── convert.py                # Main conversion pipeline
│   │   │   └── audio.py                  # Audio file serving
│   │   ├── services/                     # Business logic layer
│   │   │   ├── tts_engine.py             # Core Piper TTS engine (async)
│   │   │   ├── preview_tts.py            # Preview TTS service (sync)
│   │   │   ├── text_extractor.py         # PDF/EPUB text extraction
│   │   │   ├── text_processor.py         # Text cleaning & chunking
│   │   │   ├── audio_processor.py        # WAV file post-processing
│   │   │   └── voice_manager.py          # Voice model management
│   │   ├── models/                       # Pydantic data models
│   │   │   ├── voice.py                  # Voice schemas & metadata
│   │   │   └── schemas.py                # API request/response models
│   │   ├── core/                         # Configuration & exceptions
│   │   │   ├── config.py                 # Settings with Pydantic BaseSettings
│   │   │   ├── exceptions.py             # Custom exception classes
│   │   │   └── startup_checks.py         # System validation on startup
│   │   └── utils/                        # Utility modules
│   ├── tests/                            # Testing suite with pytest
│   │   ├── conftest.py                   # pytest configuration & fixtures
│   │   ├── unit/                         # Unit tests
│   │   │   ├── test_config.py            # Configuration tests
│   │   │   ├── test_voice_manager.py     # Voice management tests
│   │   │   └── test_audio_routes.py      # Audio endpoint tests
│   │   ├── integration/                  # Integration tests
│   │   │   └── test_voice_api.py         # Voice API integration tests
│   │   ├── test_api/                     # API endpoint tests
│   │   │   └── test_preview.py           # Preview endpoint tests
│   │   ├── test_services/                # Service layer tests
│   │   │   ├── test_tts_engine.py        # TTS engine tests
│   │   │   └── test_voice_service.py     # Voice service tests
│   │   └── fixtures/                     # Test fixtures & sample data
│   ├── voices/                           # TTS voice models (7 French voices)
│   │   └── fr/fr_FR/                     # French voices directory
│   │       ├── siwis/                    # Siwis dataset
│   │       │   ├── low/                  # fr_FR-siwis-low.onnx + .json
│   │       │   └── medium/               # fr_FR-siwis-medium.onnx + .json
│   │       ├── tom/medium/               # fr_FR-tom-medium.onnx + .json
│   │       ├── gilles/low/               # fr_FR-gilles-low.onnx + .json
│   │       ├── mls/medium/               # fr_FR-mls-medium.onnx + .json
│   │       ├── mls_1840/low/             # fr_FR-mls_1840-low.onnx + .json
│   │       └── upmc/medium/              # fr_FR-upmc-medium.onnx + .json
│   ├── storage/                          # File storage directories
│   │   ├── uploads/                      # User uploaded files (PDF/EPUB)
│   │   ├── outputs/                      # Generated audiobooks
│   │   │   └── previews/                 # Voice preview audio files
│   │   └── temp/                         # Temporary processing files
│   ├── venv/                             # Python virtual environment
│   ├── requirements.txt                  # Production dependencies
│   └── requirements-dev.txt              # Development dependencies
│
├── frontend/                             # ⚛️ Next.js 15 frontend (port 3001)
│   ├── src/                              # Source code
│   │   ├── app/                          # Next.js App Router
│   │   │   ├── globals.css               # Global styles with Tailwind CSS
│   │   │   ├── layout.tsx                # Root layout component
│   │   │   ├── page.tsx                  # Main application page
│   │   │   └── convert/[id]/page.tsx     # Conversion status tracking page
│   │   ├── components/                   # React components
│   │   │   ├── VoiceSelector.tsx         # Advanced voice selection interface
│   │   │   ├── VoicePreview.tsx          # Real-time voice preview & controls
│   │   │   ├── FileUpload.tsx            # Drag & drop file upload interface
│   │   │   └── ConversionStatus.tsx      # Progress tracking with visual indicators
│   │   ├── lib/                          # Utilities and API client
│   │   │   ├── api.ts                    # HTTP client with error handling
│   │   │   ├── types.ts                  # TypeScript type definitions
│   │   │   └── voice-types.ts            # Legacy voice types (deprecated)
│   │   └── __tests__/                    # Frontend testing with Jest
│   │       └── components/               # Component tests
│   │           ├── FileUpload.test.tsx   # File upload component tests
│   │           └── VoiceSelector.test.tsx # Voice selector tests
│   ├── public/                           # Static assets
│   │   ├── favicon.ico                   # Application favicon
│   │   ├── file.svg                      # File upload icon
│   │   ├── globe.svg                     # Globe icon
│   │   ├── next.svg                      # Next.js logo
│   │   ├── vercel.svg                    # Vercel logo
│   │   └── window.svg                    # Window icon
│   ├── node_modules/                     # Node.js dependencies (auto-generated)
│   ├── package.json                      # npm configuration & scripts
│   ├── package-lock.json                 # Dependency version lock file
│   ├── tsconfig.json                     # TypeScript strict configuration
│   ├── next.config.ts                    # Next.js configuration
│   ├── tailwind.config.ts                # Tailwind CSS configuration
│   ├── postcss.config.mjs                # PostCSS configuration
│   ├── eslint.config.mjs                 # ESLint configuration
│   ├── jest.config.js                    # Jest test configuration
│   └── jest.setup.js                     # Test setup & mocks
│
├── scripts/                              # 🛠️ Development automation scripts
│   ├── setup.sh                         # Complete project setup
│   ├── dev.sh                           # Start both backend & frontend
│   ├── backend.sh                       # Backend only startup
│   ├── frontend.sh                      # Frontend only startup
│   ├── voices.sh                        # Voice model management
│   ├── build.sh                         # Production build process
│   ├── test.sh                          # Run all tests
│   ├── clean.sh                         # Clean build artifacts
│   ├── fix-imports.sh                   # Fix Python import issues
│   └── diagnosis.sh                     # System health diagnostics
│
├── docs/                                 # 📚 Project documentation
│   └── structure.md                     # This file (project architecture)
│
├── docker/                               # 🐳 Docker configuration (optional)
│
├── Makefile                              # 🔨 Development shortcuts
├── README.md                             # 📖 Main project documentation
├── FINAL_README.md                       # 📄 Project completion summary (French)
├── tts.py                                # 📦 Legacy standalone script
└── .gitignore                            # 📝 Git ignore rules
```

## 🎯 Core Architecture Components

### ⚡ Backend - FastAPI with Piper TTS Integration

#### 🛣️ API Layer (REST Endpoints)

- **`voice.py`**: Complete voice management system with 7 French voices
  - `GET /api/voice/list` - Voice inventory with metadata
  - `GET /api/voice/{voice_id}` - Individual voice details
  - `GET /api/voice/validate/{voice_id}` - Voice availability check

- **`preview.py`**: Real-time voice testing and preview system
  - `GET /api/preview/voices` - Voices with recommendations
  - `POST /api/preview/tts` - Generate voice preview
  - `GET /api/preview/parameters/defaults` - Default TTS parameters
  - `GET /api/preview/audio/{preview_id}` - Serve preview audio

- **`upload.py`**: File processing for PDF/EPUB documents
  - `POST /api/upload/file` - Multipart file upload with validation

- **`convert.py`**: Main audiobook conversion pipeline
  - `POST /api/convert/start` - Start conversion job
  - `GET /api/convert/status/{job_id}` - Real-time progress tracking

- **`audio.py`**: Generated audio file serving
  - `GET /api/audio/{job_id}` - Stream audio file
  - `GET /api/audio/{job_id}/download` - Force download

#### ⚙️ Service Layer (Business Logic)

- **`tts_engine.py`**: Core Piper TTS engine with async processing
- **`preview_tts.py`**: Lightweight TTS for real-time previews
- **`text_extractor.py`**: PDF/EPUB text extraction with PyPDF2 + EbookLib
- **`text_processor.py`**: Text cleaning and intelligent chunking
- **`audio_processor.py`**: WAV file concatenation and post-processing
- **`voice_manager.py`**: Voice model discovery and metadata management

#### 🎭 Voice System (7 French Voices)

- **Female Voices**: Siwis (low/medium), MLS, MLS_1840
- **Male Voices**: Tom (medium), Gilles (low)
- **Neutral**: UPMC (medium)
- **Quality Levels**: Low (fast), Medium (balanced), High (best quality)
- **Metadata**: Usage recommendations, technical specifications

#### 📦 Data Models (Pydantic v2)

- **Type Safety**: Strict validation with comprehensive error messages
- **API Schemas**: Request/response models with OpenAPI documentation
- **Configuration**: Environment-based settings with BaseSettings
- **Error Handling**: Custom exceptions with user-friendly messages

### 🎨 Frontend - Next.js 15 with Modern UI/UX

#### 🧭 App Router Architecture

- **Server Components**: Fast initial page loads with SSR
- **Client Components**: Interactive UI with React hooks
- **Dynamic Routing**: `/convert/[id]` for conversion status tracking
- **TypeScript Integration**: Strict mode with comprehensive type safety

#### 🧩 Component System

- **`VoiceSelector.tsx`**: Advanced voice selection with filtering & sorting
  - 7 French voices with metadata display
  - Filter by gender, quality, usage recommendations
  - Sort by name, quality, file size
  - Visual voice cards with real-time preview

- **`VoicePreview.tsx`**: Real-time voice testing interface
  - Live TTS preview generation
  - Advanced parameter controls (speed, expressiveness, etc.)
  - Smart presets: audiobook, news, storytelling
  - Integrated audio player with playback controls

- **`FileUpload.tsx`**: Modern drag & drop interface
  - File validation (PDF/EPUB, 50MB max)
  - Visual feedback with progress simulation
  - Error handling with detailed messages
  - Responsive design for mobile/desktop

- **`ConversionStatus.tsx`**: Progress tracking with visual indicators
  - Real-time status polling every 2 seconds
  - Multi-step progress visualization
  - Conversion time tracking
  - Download functionality for completed audio

#### 🎯 State & API Management

- **Custom API Client**: Comprehensive error handling with retry logic
- **React Hooks**: useState, useEffect for local component state
- **Real-time Updates**: Polling-based status updates
- **Type Safety**: Full TypeScript integration with backend schemas

#### 🎨 Styling & Design

- **Tailwind CSS**: Utility-first styling with custom gradients
- **Responsive Design**: Mobile-first approach with breakpoint optimization
- **Modern Animations**: Smooth transitions and micro-interactions
- **Accessibility**: WCAG compliant with keyboard navigation

### 🚀 Development Workflow & Quality Assurance

#### 🔧 Automation Scripts

- **`setup.sh`**: One-command project initialization
- **`dev.sh`**: Start both backend (8001) & frontend (3001) servers
- **`test.sh`**: Run comprehensive test suite (backend + frontend)
- **`voices.sh`**: Voice model management and validation
- **`diagnosis.sh`**: System health check and troubleshooting

#### 🧪 Testing Strategy

**Backend Testing (Python + pytest)**:
- Unit tests for core services and utilities
- Integration tests for API endpoints
- Voice system testing with mock TTS generation
- Configuration validation tests

**Frontend Testing (TypeScript + Jest)**:
- Component testing with React Testing Library
- API client testing with mocked responses
- User interaction testing for file upload
- Voice selector functionality tests

#### 🔍 Code Quality Tools

**Backend**:
- **FastAPI**: Automatic OpenAPI documentation
- **Pydantic v2**: Runtime type validation
- **pytest**: Comprehensive testing framework
- **Python typing**: Full type hints throughout

**Frontend**:
- **TypeScript Strict**: Maximum type safety
- **ESLint**: Code quality and consistency
- **Jest**: Testing framework with coverage
- **Next.js**: Built-in optimization and bundling

#### 📊 Performance & Monitoring

- **Voice Preview**: ~2-3 seconds generation time
- **File Processing**: Support for up to 50MB documents
- **Memory Management**: Automatic cleanup of temporary files
- **Health Checks**: `/health` endpoint with system validation
- **Error Tracking**: Comprehensive error handling with user-friendly messages

## 📊 Data Flow Architecture

### Complete User Workflow

1. **Homepage** (`app/page.tsx`)

   - VoicePreview component → test voice with custom parameters
   - FileUpload component → upload PDF/EPUB with validation

2. **File Upload** (`api/routes/upload.py`)

   - Multipart form handling with size/type validation
   - Secure filename sanitization + virus scanning
   - Storage in `storage/uploads/` with unique identifiers
   - Return structured metadata (file_id, size, type)

3. **Conversion Start** (`api/routes/convert.py`)

   - Text extraction with format-specific parsers
   - Intelligent text cleaning + chapter detection
   - Background job creation with unique job_id
   - Real-time progress updates via WebSocket or polling

4. **TTS Processing** (`services/tts_engine.py`)

   - Text chunking for optimal voice synthesis
   - Piper TTS synthesis with custom voice parameters
   - Audio concatenation with seamless transitions
   - Quality validation + format optimization

5. **Status Monitoring** (`convert/[id]/page.tsx`)

   - Real-time polling of job status
   - Progress visualization with estimated completion
   - Error handling with user-friendly messages
   - Automatic refresh + notification system

6. **Audio Download** (`api/routes/audio.py`)
   - Streaming file downloads for large files
   - HTTP range support for resumable downloads
   - Proper MIME types + cache headers
   - Usage tracking + analytics

### Voice Preview Workflow

1. **Voice Discovery** (`services/voice_service.py`)

   - Automatic scanning of voices/ directory
   - Metadata parsing from .onnx.json files
   - Quality assessment + compatibility checking
   - Caching for performance optimization

2. **Preview Generation** (`api/routes/preview.py`)

   - Lightweight TTS for 30-second samples
   - Parameter customization (speed, pitch, pauses)
   - Temporary file management with auto-cleanup
   - Real-time audio streaming to frontend

3. **User Selection** (`components/VoiceSelector.tsx`)
   - Voice filtering by language/quality/usage
   - Live preview playback with custom controls
   - Parameter adjustment with immediate feedback
   - Selection persistence across sessions

## 🔧 Configuration Management

### Environment Variables

#### Backend Configuration (.env)

```bash
# Application Settings
DEBUG=false
APP_NAME="Audio Book Converter"
VERSION="1.0.0"

# Server Configuration
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=["http://localhost:3000"]

# TTS Configuration
PIPER_EXECUTABLE=piper
DEFAULT_VOICE_MODEL=fr_FR-siwis-low
DEFAULT_LENGTH_SCALE=1.0
DEFAULT_NOISE_SCALE=0.667
SENTENCE_SILENCE=0.35

# File Processing
MAX_FILE_SIZE=52428800  # 50MB
MAX_CHUNK_CHARS=1500
ALLOWED_EXTENSIONS=.pdf,.epub

# Storage Paths (auto-detected in dev)
VOICES_BASE_PATH=backend/voices
STORAGE_BASE_PATH=backend/storage
```

#### Frontend Configuration (.env.local)

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Feature Flags
NEXT_PUBLIC_VOICE_PREVIEW=true
NEXT_PUBLIC_ANALYTICS_ENABLED=false

# UI Configuration
NEXT_PUBLIC_MAX_FILE_SIZE=52428800
NEXT_PUBLIC_SUPPORTED_FORMATS=pdf,epub
```

### Build Configuration

#### Next.js Configuration (next.config.ts)

```typescript
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    typedRoutes: true,
  },
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
```

#### Docker Configuration (Dockerfile)

```dockerfile
# Multi-stage build for production optimization
FROM python:3.11-slim as backend
FROM node:18-alpine as frontend
FROM nginx:alpine as production

# Optimized for size + security + performance
```

## 🧪 Testing Strategy

### Backend Testing (Python)

```bash
# Unit tests with pytest
backend/tests/test_services/test_tts_engine.py
backend/tests/test_api/test_upload.py

# Integration tests
backend/tests/integration/test_full_workflow.py

# Performance tests
backend/tests/performance/test_large_files.py
```

### Frontend Testing (TypeScript)

```bash
# Component tests with Testing Library
frontend/src/__tests__/components/FileUpload.test.tsx

# API integration tests
frontend/src/__tests__/lib/api.test.ts

# E2E tests with Playwright (optional)
frontend/e2e/conversion-workflow.spec.ts
```

### Quality Gates

- **Coverage**: Minimum 80% for critical paths
- **Performance**: < 2s API response times
- **Security**: OWASP Top 10 compliance
- **Accessibility**: WCAG 2.1 AA compliance

## 🚀 Deployment Architecture

### Development Environment

- **Hot reload**: Automatic code refresh
- **Live debugging**: VSCode integration
- **Database**: Local file storage
- **Monitoring**: Console logs + local metrics

### Production Environment (CapRover)

- **Load balancing**: Automatic scaling
- **SSL/TLS**: Let's Encrypt integration
- **Monitoring**: Health checks + alerting
- **Backup**: Automated data persistence

### CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: Test & Deploy
on: [push, pull_request]
jobs:
  test:
    - Backend: pytest + mypy + ruff
    - Frontend: Jest + ESLint + TypeScript
    - Integration: Full workflow testing
  deploy:
    - Build: Docker multi-stage
    - Deploy: CapRover automatic
    - Monitor: Health check validation
```

## 🔍 Monitoring and Observability

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
