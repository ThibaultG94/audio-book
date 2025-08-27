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
│   │   │   ├── dependencies.py           # Common FastAPI dependencies
│   │   │   └── routes/                   # HTTP endpoints
│   │   │       ├── __init__.py           # Routes exports
│   │   │       ├── upload.py             # PDF/EPUB file upload endpoints
│   │   │       ├── convert.py            # TTS conversion with background jobs
│   │   │       ├── audio.py              # Generated audio file serving
│   │   │       └── preview.py            # TTS preview for voice testing
│   │   ├── services/                     # Business logic layer
│   │   │   ├── __init__.py               # Services exports
│   │   │   ├── text_extractor.py         # PDF/EPUB → text extraction
│   │   │   ├── text_processor.py         # Text cleaning + chunking
│   │   │   ├── tts_engine.py             # Piper TTS interface
│   │   │   ├── audio_processor.py        # WAV concatenation
│   │   │   ├── voice_service.py          # Voice management and discovery
│   │   │   └── preview_service.py        # Lightweight TTS for previews
│   │   ├── models/                       # Pydantic schemas and enums
│   │   │   ├── __init__.py               # Models exports
│   │   │   ├── voice.py                  # Voice-related schemas
│   │   │   ├── upload.py                 # File upload schemas
│   │   │   ├── convert.py                # Conversion schemas
│   │   │   └── common.py                 # Shared models
│   │   ├── core/                         # System configuration
│   │   │   ├── __init__.py               # Core exports
│   │   │   ├── config.py                 # Pydantic settings + environment
│   │   │   ├── exceptions.py             # Custom exceptions
│   │   │   ├── logging.py                # Structured logging setup
│   │   │   └── startup_checks.py         # System validation on startup
│   │   └── utils/                        # General utilities
│   │       ├── __init__.py               # Utils exports
│   │       ├── file_utils.py             # File operations
│   │       └── validation.py             # Data validation helpers
│   ├── tests/                            # Backend testing suite
│   │   ├── __init__.py                   # Tests package init
│   │   ├── conftest.py                   # pytest configuration + fixtures
│   │   ├── test_api/                     # API endpoint tests
│   │   │   ├── __init__.py               # API tests init
│   │   │   ├── test_upload.py            # Upload endpoint tests
│   │   │   ├── test_convert.py           # Conversion endpoint tests
│   │   │   └── test_preview.py           # Preview endpoint tests
│   │   ├── test_services/                # Service layer tests
│   │   │   ├── __init__.py               # Service tests init
│   │   │   ├── test_tts_engine.py        # TTS engine tests
│   │   │   ├── test_text_processor.py    # Text processing tests
│   │   │   └── test_voice_service.py     # Voice service tests
│   │   └── test_utils/                   # Utility function tests
│   │       └── test_file_utils.py        # File operation tests
│   ├── voices/                           # TTS voice models
│   │   └── fr/                           # French voices
│   │       └── fr_FR/                    # French (France) locale
│   │           └── siwis/                # Siwis dataset voices
│   │               ├── low/              # Low quality (faster)
│   │               │   ├── fr_FR-siwis-low.onnx      # Voice model
│   │               │   └── fr_FR-siwis-low.onnx.json # Voice metadata
│   │               ├── medium/           # Medium quality
│   │               └── high/             # High quality (slower)
│   ├── storage/                          # File storage directories
│   │   ├── uploads/                      # User uploaded files (PDF/EPUB)
│   │   ├── outputs/                      # Generated audio files
│   │   └── temp/                         # Temporary processing files
│   ├── venv/                             # Python virtual environment
│   ├── requirements.txt                  # Production dependencies
│   ├── requirements-dev.txt              # Development dependencies (pytest, etc.)
│   ├── .env                              # Environment variables (local)
│   ├── .env.example                      # Environment template
│   └── .gitignore                        # Backend-specific Git ignores
│
├── frontend/                             # ⚛️ Next.js frontend
│   ├── src/                              # Source code
│   │   ├── app/                          # Next.js App Router
│   │   │   ├── globals.css               # Global styles (TailwindCSS)
│   │   │   ├── layout.tsx                # Root layout component
│   │   │   ├── page.tsx                  # Homepage (upload + voice preview)
│   │   │   ├── convert/                  # Conversion status pages
│   │   │   │   └── [id]/                 # Dynamic route for job status
│   │   │   │       └── page.tsx          # Conversion status page
│   │   │   └── error.tsx                 # Error page component
│   │   ├── components/                   # Reusable UI components
│   │   │   ├── ui/                       # shadcn/ui base components
│   │   │   │   ├── button.tsx            # Button component
│   │   │   │   ├── input.tsx             # Input component
│   │   │   │   └── progress.tsx          # Progress bar component
│   │   │   ├── FileUpload.tsx            # Drag & drop file upload
│   │   │   ├── VoicePreview.tsx          # Voice testing with live TTS
│   │   │   ├── VoiceSelector.tsx         # Voice selection component
│   │   │   ├── ConversionStatus.tsx      # Real-time conversion progress
│   │   │   └── AudioPlayer.tsx           # Audio playback component
│   │   ├── lib/                          # Utilities and API client
│   │   │   ├── api.ts                    # HTTP client for backend API
│   │   │   ├── types.ts                  # Shared TypeScript interfaces
│   │   │   └── utils.ts                  # General utility functions
│   │   ├── hooks/                        # Custom React hooks
│   │   │   ├── useUpload.ts              # File upload logic
│   │   │   ├── useConversion.ts          # Conversion status polling
│   │   │   └── useVoices.ts              # Voice data management
│   │   └── __tests__/                    # Frontend Jest tests
│   │       ├── components/               # Component tests
│   │       │   ├── FileUpload.test.tsx   # Upload component tests
│   │       │   └── VoiceSelector.test.tsx # Voice selector tests
│   │       └── lib/                      # Library tests
│   │           └── api.test.ts           # API client tests
│   ├── public/                           # Static assets
│   │   ├── favicon.ico                   # Application favicon
│   │   └── logo.svg                      # Application logo
│   ├── node_modules/                     # Node.js dependencies
│   ├── package.json                      # npm configuration + scripts
│   ├── package-lock.json                 # Dependency lock file
│   ├── tsconfig.json                     # TypeScript configuration
│   ├── next.config.ts                    # Next.js configuration
│   ├── tailwind.config.js                # TailwindCSS configuration
│   ├── postcss.config.mjs                # PostCSS configuration
│   ├── eslint.config.mjs                 # ESLint configuration
│   ├── jest.config.js                    # Jest test configuration
│   ├── jest.setup.js                     # Test setup + mocks
│   ├── .env.local                        # Frontend environment variables
│   └── .gitignore                        # Frontend-specific Git ignores
│
├── scripts/                              # 🛠️ DevOps automation scripts
│   ├── setup.sh                          # 🚀 Complete initial setup
│   ├── dev.sh                            # 🔥 Development environment startup
│   ├── backend.sh                        # 🐍 Backend only startup
│   ├── frontend.sh                       # ⚛️  Frontend only startup
│   ├── install-piper.sh                  # 🆕 Automatic Piper TTS installation
│   ├── download-voices.sh                # 📥 Download additional voice models
│   ├── fix-imports.sh                    # 🔧 Fix Python import issues
│   ├── build.sh                          # 🏗️ Production build
│   ├── test.sh                           # 🧪 Comprehensive testing
│   ├── clean.sh                          # 🧹 Clean build artifacts
│   └── diagnosis.sh                      # 🔍 System diagnostic tool
│
├── docs/                                 # 📚 Project documentation
│   ├── structure.md                      # 📋 This file (detailed structure)
│   ├── API.md                            # REST API documentation
│   ├── DEPLOYMENT.md                     # Production deployment guide
│   └── CONTRIBUTING.md                   # Contribution guidelines
│
├── docker/                               # 🐳 Docker configuration (future)
│   ├── Dockerfile                        # Multi-stage production build
│   ├── docker-compose.yml                # Local development setup
│   └── .dockerignore                     # Docker ignore rules
│
├── .github/                              # 🔧 GitHub configuration
│   ├── workflows/                        # CI/CD workflows
│   │   ├── test.yml                      # Automated testing
│   │   └── deploy.yml                    # Automated deployment
│   ├── ISSUE_TEMPLATE/                   # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md          # PR template
│
├── captain-definition                     # ⚓ CapRover deployment config
├── Dockerfile                            # 🐳 Production Docker image
├── Makefile                              # 🔨 Development commands
├── .env.example                          # 🔐 Environment variables template
├── .gitignore                            # 📝 Git ignore rules
├── README.md                             # 📖 Project overview
├── LICENSE                               # ⚖️  MIT License
│
└── legacy/                               # 📦 Legacy files (for reference)
    ├── tts.py                            # Original Python script
    └── venv/                             # Legacy virtual environment at root
```

## 🏗️ Core Architecture Components

### Backend - Modern FastAPI Architecture

#### API Layer (RESTful Design)

- **upload.py**: Multipart file upload with validation + storage
- **convert.py**: Background TTS conversion jobs with status tracking
- **audio.py**: Streaming audio file downloads with proper headers
- **preview.py**: Real-time voice testing for user experience

#### Service Layer (Business Logic)

- **text_extractor.py**: PyPDF2 + EbookLib + BeautifulSoup parsing
- **text_processor.py**: Text cleaning + intelligent chunking
- **tts_engine.py**: Piper TTS integration with async processing
- **voice_service.py**: Voice model discovery + metadata management
- **audio_processor.py**: WAV file concatenation + format conversion

#### Data Layer (Pydantic Models)

- **Strict validation**: All API inputs/outputs validated
- **Type safety**: Full TypeScript-style typing for Python
- **Error handling**: Custom exceptions with detailed messages
- **Configuration**: 12-Factor App pattern with environment variables

### Frontend - Modern Next.js Architecture

#### App Router (Next.js 13+)

- **Server components**: SEO-friendly + fast initial load
- **Client components**: Interactive UI with React hooks
- **Dynamic routing**: Real-time conversion status pages
- **API routes**: Optional proxy layer (or direct backend calls)

#### Component Architecture

- **Atomic design**: ui/ → components/ → pages/ hierarchy
- **TypeScript strict**: Full type safety with backend integration
- **TailwindCSS**: Utility-first styling + responsive design
- **Accessibility**: WCAG compliant components

#### State Management

- **React Query**: Server state management + caching
- **Custom hooks**: Reusable logic (useUpload, useConversion)
- **Context API**: Global state when needed
- **Local storage**: User preferences persistence

### Development Workflow

#### Automation Scripts

- **setup.sh**: Zero-config development environment
- **dev.sh**: Hot-reload development servers
- **test.sh**: Comprehensive testing pipeline
- **build.sh**: Production-ready Docker images

#### Quality Assurance

- **Backend**: pytest + coverage + mypy + ruff
- **Frontend**: Jest + Testing Library + ESLint + TypeScript
- **Integration**: End-to-end API testing
- **Performance**: Load testing + bundle analysis

#### DevOps Integration

- **Docker**: Multi-stage builds for efficient deployment
- **CapRover**: One-click deployment with automatic SSL
- **GitHub Actions**: CI/CD pipeline with testing + deployment
- **Monitoring**: Health checks + structured logging

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
