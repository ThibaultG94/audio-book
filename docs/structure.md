# 📁 Complete Audio Book Converter Project Structure

## Architecture Overview

The Audio Book Converter is a full-stack application with advanced voice management capabilities, built using modern Python and Node.js technologies.

```
audio-book/                               # 🏠 Project root directory
├── backend/                              # 🐍 Python FastAPI backend
│   ├── app/                              # Main application package
│   │   ├── __init__.py                   # App initialization (version, metadata)
│   │   ├── main.py                       # FastAPI application entry point with all routes
│   │   ├── api/                          # REST API layer
│   │   │   ├── __init__.py               # API package initialization
│   │   │   └── routes/                   # HTTP endpoints modules
│   │   │       ├── __init__.py           # Routes package exports
│   │   │       ├── upload.py             # File upload endpoints (PDF/EPUB)
│   │   │       ├── convert.py            # TTS conversion with background job management
│   │   │       ├── audio.py              # Generated audio file serving and streaming
│   │   │       └── preview.py            # Enhanced voice preview system with parameters
│   │   ├── services/                     # Business logic layer
│   │   │   ├── __init__.py               # Services package exports
│   │   │   ├── text_extractor.py         # PDF/EPUB → text extraction (PyPDF2, ebooklib)
│   │   │   ├── text_processor.py         # Text cleaning, chunking, French optimization
│   │   │   ├── tts_engine.py             # Piper TTS interface with subprocess management
│   │   │   ├── audio_processor.py        # WAV concatenation and audio manipulation
│   │   │   ├── preview_tts.py            # Enhanced TTS for previews with French accent handling
│   │   │   └── voice_manager.py          # Advanced voice management system with metadata
│   │   ├── models/                       # Pydantic schemas and data models
│   │   │   ├── __init__.py               # Models package exports
│   │   │   └── schemas.py                # Request/Response models, enums, validation
│   │   ├── core/                         # System configuration and utilities
│   │   │   ├── __init__.py               # Core package exports
│   │   │   ├── config.py                 # Pydantic settings with voice auto-detection
│   │   │   ├── exceptions.py             # Custom exception hierarchy
│   │   │   └── startup_checks.py         # System validation (Piper TTS, voice models)
│   │   └── utils/                        # General utilities and helpers
│   │       └── __init__.py
│   ├── tests/                            # Complete test suite
│   │   ├── __init__.py
│   │   ├── conftest.py                   # Pytest configuration and shared fixtures
│   │   ├── fixtures/                     # Test data and mock fixtures
│   │   │   └── __init__.py
│   │   ├── unit/                         # Service unit tests
│   │   │   ├── __init__.py
│   │   │   ├── test_text_extractor.py    # Text extraction tests
│   │   │   ├── test_text_processor.py    # Text processing tests
│   │   │   ├── test_audio_routes.py      # Audio endpoints tests
│   │   │   └── test_voice_manager.py     # Voice management system tests
│   │   └── integration/                  # End-to-end integration tests
│   │       ├── __init__.py
│   │       └── test_voice_api.py         # Complete voice API workflow tests
│   ├── storage/                          # Runtime file storage
│   │   ├── uploads/                      # Uploaded PDF/EPUB files (temporary)
│   │   ├── outputs/                      # Generated WAV audio files
│   │   │   └── previews/                 # Voice preview audio files (temporary)
│   ├── voices/                           # TTS voice models with hierarchical structure
│   │   ├── voice_metadata.json           # Comprehensive voice metadata database
│   │   └── fr/                           # French language voices
│   │       └── fr_FR/                    # French (France) locale
│   │           ├── siwis/                # Siwis dataset voices (female)
│   │           │   ├── low/              # Low quality (fast processing)
│   │           │   │   ├── fr_FR-siwis-low.onnx        # Neural voice model
│   │           │   │   └── fr_FR-siwis-low.onnx.json   # Voice metadata
│   │           │   ├── medium/           # Medium quality (balanced)
│   │           │   │   ├── fr_FR-siwis-medium.onnx
│   │           │   │   └── fr_FR-siwis-medium.onnx.json
│   │           └── upmc/                 # UPMC dataset (multi-speaker)
│   │               └── medium/
│   │                   ├── fr_FR-upmc-medium.onnx      # Multi-speaker model
│   │                   └── fr_FR-upmc-medium.onnx.json # Speaker metadata (Jessica+Pierre)
│   ├── venv/                             # Python virtual environment
│   ├── requirements.txt                  # Production dependencies (FastAPI, Piper, etc.)
│   └── requirements-dev.txt              # Development dependencies (pytest, ruff, mypy)
│
├── frontend/                             # ⚛️ Next.js 15 TypeScript frontend
│   ├── .next/                            # Next.js build output (generated)
│   ├── node_modules/                     # Node.js dependencies (generated)
│   ├── public/                           # Static assets
│   ├── src/                              # TypeScript source code
│   │   ├── __tests__/                    # Frontend test suite
│   │   │   └── components/
│   │   │       └── FileUpload.test.tsx   # Component testing with React Testing Library
│   │   ├── app/                          # Next.js App Router (13+ structure)
│   │   │   ├── convert/[id]/             # Dynamic conversion status pages
│   │   │   │   └── page.tsx              # Individual conversion tracking and progress
│   │   │   ├── favicon.ico               # Application favicon
│   │   │   ├── globals.css               # Global TailwindCSS styles and theme
│   │   │   ├── layout.tsx                # Root layout (fonts, metadata, providers)
│   │   │   └── page.tsx                  # Homepage with voice preview and file upload
│   │   ├── components/                   # Reusable React components
│   │   │   ├── ConversionStatus.tsx      # Conversion progress display with polling
│   │   │   ├── FileUpload.tsx            # Drag & drop file upload with validation
│   │   │   ├── VoicePreview.tsx          # Advanced voice testing interface
│   │   │   └── VoiceSelector.tsx         # Comprehensive voice selection with filters
│   │   └── lib/                          # Utilities and API integration
│   │       ├── api.ts                    # HTTP client for backend API communication
│   │       └── types.ts                  # Shared TypeScript interfaces and types
│   ├── .gitignore                        # Frontend-specific Git ignore rules
│   ├── eslint.config.mjs                 # ESLint configuration (ES modules)
│   ├── jest.config.js                    # Jest testing framework configuration
│   ├── jest.setup.js                     # Test environment setup and mocks
│   ├── next.config.ts                    # Next.js configuration (TypeScript)
│   ├── next-env.d.ts                     # Next.js TypeScript declarations (generated)
│   ├── package.json                      # npm dependencies and scripts
│   ├── postcss.config.mjs                # PostCSS configuration for TailwindCSS
│   ├── README.md                         # Frontend-specific documentation
│   └── tsconfig.json                     # TypeScript compiler configuration
│
├── scripts/                              # 🛠️ DevOps and automation scripts
│   ├── setup.sh                          # 🚀 Complete initial project setup
│   ├── dev.sh                            # 🔥 Development environment startup (backend + frontend)
│   ├── backend.sh                        # 🐍 Backend only startup script
│   ├── frontend.sh                       # ⚛️ Frontend only startup script
│   ├── install-voices.sh                 # 🎤 Comprehensive voice installation system
│   ├── diagnosis.sh                      # 🔍 System diagnostic and troubleshooting
│   ├── voices.sh                         # 🎵 Voice structure validation and testing
│   ├── fix-imports.sh                    # 🔧 Python import issue resolution
│   ├── build.sh                          # 🏗️ Production build preparation
│   ├── test.sh                           # 🧪 Comprehensive test suite execution
│   └── clean.sh                          # 🧹 Build artifacts and cache cleanup
│
├── docs/                                 # 📚 Project documentation
│   └── structure.md                      # 📋 This file - complete project structure
│
├── docker/                               # 🐳 Docker configuration (future expansion)
│   ├── Dockerfile                        # Production multi-stage image definition
│   └── docker-compose.dev.yml           # Development environment with services
│
├── .gitignore                            # 🚫 Global Git ignore rules
├── Makefile                              # ⚡ Quick development command shortcuts
├── captain-definition                    # 🚢 CapRover deployment configuration
└── README.md                             # 📖 Main project documentation and quick start
```

## 🔧 Key Components Deep Dive

### Backend Architecture (`backend/app/`)

#### API Layer (`api/routes/`)

- **upload.py**: Handles multipart file uploads with size/type validation
- **convert.py**: Manages TTS conversion jobs with background processing and status polling
- **audio.py**: Serves generated audio files with streaming and security checks
- **preview.py**: **Advanced voice preview system** with parameter customization, voice metadata, and installation guides

#### Services Layer (`services/`)

- **text_extractor.py**: PDF (PyPDF2) and EPUB (ebooklib) text extraction with error handling
- **text_processor.py**: Text cleaning, normalization, and intelligent chunking for TTS
- **tts_engine.py**: Piper TTS subprocess interface with timeout and error management
- **audio_processor.py**: WAV file concatenation with customizable pauses
- **preview_tts.py**: **Enhanced preview engine** with French text preprocessing and accent preservation
- **voice_manager.py**: **Comprehensive voice management** with metadata, filtering, recommendations, and validation

#### Core System (`core/`)

- **config.py**: Pydantic settings with environment variable loading and voice auto-detection
- **exceptions.py**: Structured exception hierarchy for different failure modes
- **startup_checks.py**: System validation (Piper TTS availability, voice model integrity)

### Frontend Architecture (`frontend/src/`)

#### App Router (`app/`)

- **page.tsx**: Homepage with integrated voice preview and file upload interface
- **layout.tsx**: Global layout with Geist fonts, TailwindCSS, and metadata
- **convert/[id]/page.tsx**: Dynamic conversion tracking with real-time status updates

#### Components (`components/`)

- **VoicePreview.tsx**: **Advanced voice testing interface** with parameter sliders, text input, and audio playback
- **VoiceSelector.tsx**: **Comprehensive voice catalog** with filtering, metadata display, and recommendations
- **FileUpload.tsx**: Drag & drop upload with react-dropzone integration
- **ConversionStatus.tsx**: Real-time conversion progress with polling and download links

#### Integration Layer (`lib/`)

- **api.ts**: Type-safe HTTP client with error handling and retry logic
- **types.ts**: Shared TypeScript interfaces matching backend Pydantic schemas

### Voice Management System

#### Voice Structure (`backend/voices/`)

```
voices/
├── voice_metadata.json           # Central metadata database
└── fr/fr_FR/                    # Language/locale hierarchy
    ├── siwis/                   # Dataset organization
    │   ├── low/                 # Quality levels
    │   ├── medium/
    │   └── high/
    ├── tom/medium/              # Male voice (Tom)
    ├── bernard/high/            # Mature male voice
    └── upmc/medium/             # Multi-speaker (Jessica + Pierre)
```

#### Voice Features

- **Metadata System**: Comprehensive voice information (gender, quality, usage recommendations)
- **Quality Levels**: Low (fast), Medium (balanced), High (premium)
- **Usage Recommendations**: Audiobook, news, storytelling, educational, documentary
- **Speaker Information**: Gender, age range, voice style, accent details
- **Multi-Speaker Support**: Dual-gender voices with individual speaker metadata

### Testing Infrastructure (`backend/tests/`)

#### Test Organization

- **Unit Tests** (`unit/`): Individual service and component testing
- **Integration Tests** (`integration/`): End-to-end API workflow validation
- **Fixtures** (`fixtures/`): Reusable test data and mock objects
- **Configuration** (`conftest.py`): Pytest setup, fixtures, and shared utilities

#### Test Coverage

- Voice management system validation
- API endpoint functionality and error handling
- Text processing and TTS engine integration
- File upload and conversion workflows

### Automation Scripts (`scripts/`)

#### Development Scripts

- **setup.sh**: Complete project initialization (venv, deps, directories)
- **dev.sh**: Concurrent development server startup with voice system check
- **diagnosis.sh**: Comprehensive system diagnostic and troubleshooting

#### Voice Management Scripts

- **install-voices.sh**: **Advanced voice installation** with presets (default, premium, minimal, all)
- **voices.sh**: Voice structure validation, Piper testing, and configuration updates

#### Quality Assurance Scripts

- **test.sh**: Complete test suite execution (backend + frontend)
- **clean.sh**: Build artifacts and cache cleanup
- **build.sh**: Production build preparation

## 🔄 Data Flow and System Integration

### Complete User Workflow

1. **Voice Selection & Preview** (`VoiceSelector` + `VoicePreview`)

   - Browse available voices with metadata filtering
   - Test voices with custom text and parameters
   - Real-time audio generation and playback
   - Parameter optimization (speed, expressivity, pauses)

2. **File Upload** (`FileUpload` → `upload.py`)

   - Drag & drop PDF/EPUB files
   - Client-side validation (type, size)
   - Server-side security checks and storage

3. **TTS Conversion** (`convert.py` + services)

   - Text extraction with error handling
   - Intelligent text chunking and cleaning
   - Voice-optimized synthesis with selected parameters
   - Background job processing with progress tracking

4. **Status Monitoring** (`ConversionStatus`)

   - Real-time progress polling
   - Error reporting and retry mechanisms
   - Completion notifications

5. **Audio Delivery** (`audio.py`)
   - Secure file serving with streaming
   - Download optimization and caching
   - Temporary file cleanup

### Voice System Workflow

1. **Voice Discovery** (`VoiceManager.load_metadata()`)

   - Scan installed voice models
   - Parse ONNX metadata files
   - Generate comprehensive voice database

2. **Voice Filtering** (`VoiceSelector`)

   - Gender-based filtering (male, female, multi)
   - Quality-based selection (low, medium, high)
   - Usage-based recommendations (audiobook, news, etc.)

3. **Voice Validation** (`startup_checks.py`)

   - Piper TTS availability verification
   - Voice model integrity checks
   - System compatibility validation

4. **Preview Generation** (`preview_tts.py`)
   - French-optimized text preprocessing
   - Parameter-aware synthesis
   - Temporary audio file management

## 🚀 Development and Deployment

### Development Environment

- **Hot Reload**: FastAPI auto-reload + Next.js turbo dev
- **Type Safety**: mypy for Python + strict TypeScript
- **Code Quality**: ruff + ESLint with automated formatting
- **Testing**: pytest + Jest with comprehensive coverage

### Production Deployment

- **Containerization**: Multi-stage Dockerfile for optimized images
- **Platform**: CapRover PaaS with automated deployment
- **Configuration**: Environment-based settings management
- **Monitoring**: Health checks and system diagnostics

### Voice System Management

- **Installation**: Automated voice download and setup
- **Validation**: Continuous voice model integrity checks
- **Updates**: Version-controlled voice metadata system
- **Scaling**: Support for additional languages and voice providers

This structure represents a mature, production-ready application with comprehensive voice management capabilities, robust testing infrastructure, and automated deployment processes.
