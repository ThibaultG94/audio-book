# Project Structure

Complete overview of the Audio Book Converter application structure.

## 📁 Complete Project Structure

```
audio-book/
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app entry point
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── upload.py         # File upload endpoints
│   │   │   │   ├── convert.py        # TTS conversion endpoints
│   │   │   │   └── audio.py          # Audio file serving
│   │   │   └── dependencies.py       # FastAPI dependencies
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── text_extractor.py     # PDF/EPUB text extraction
│   │   │   ├── text_processor.py     # Text cleaning & chunking
│   │   │   ├── tts_engine.py         # Piper TTS integration
│   │   │   └── audio_processor.py    # WAV concatenation & processing
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py            # Pydantic models
│   │   │   └── enums.py              # Status enums, etc.
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # Settings & environment
│   │   │   ├── exceptions.py         # Custom exceptions
│   │   │   └── logger.py             # Structured logging
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── file_utils.py         # File operations
│   │       └── validation.py         # Input validation
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py               # Pytest fixtures
│   │   ├── unit/
│   │   │   ├── test_text_extractor.py
│   │   │   ├── test_text_processor.py
│   │   │   └── test_tts_engine.py
│   │   └── integration/
│   │       └── test_api.py
│   ├── voices/                       # TTS voice models
│   │   └── fr/fr_FR/siwis/low/
│   │       ├── fr_FR-siwis-low.onnx
│   │       └── fr_FR-siwis-low.onnx.json
│   ├── storage/                      # Generated audio files
│   │   ├── uploads/                  # Uploaded PDF/EPUB
│   │   └── outputs/                  # Generated WAV/MP3
│   ├── venv/                         # Python virtual environment
│   ├── requirements.txt
│   ├── requirements-dev.txt          # Dev dependencies
│   └── pyproject.toml                # Project config & tools
│
├── frontend/                         # Next.js frontend
│   ├── src/
│   │   ├── app/                      # App Router (Next.js 13+)
│   │   │   ├── layout.tsx            # Root layout
│   │   │   ├── page.tsx              # Home page
│   │   │   ├── upload/
│   │   │   │   └── page.tsx          # File upload page
│   │   │   ├── convert/
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx      # Conversion status page
│   │   │   └── player/
│   │   │       └── [id]/
│   │   │           └── page.tsx      # Audio player page
│   │   ├── components/
│   │   │   ├── ui/                   # shadcn/ui components
│   │   │   ├── FileUpload.tsx        # File upload component
│   │   │   ├── ConversionStatus.tsx  # Progress tracking
│   │   │   ├── AudioPlayer.tsx       # Audio playback
│   │   │   └── Layout.tsx            # App layout wrapper
│   │   ├── lib/
│   │   │   ├── api.ts                # API client functions
│   │   │   ├── types.ts              # TypeScript interfaces
│   │   │   ├── utils.ts              # Utility functions
│   │   │   └── validations.ts        # Form validation schemas
│   │   └── hooks/
│   │       ├── useFileUpload.ts      # File upload hook
│   │       ├── useConversionStatus.ts# Status polling hook
│   │       └── useAudioPlayer.ts     # Audio player hook
│   ├── public/
│   │   ├── icons/
│   │   └── favicon.ico
│   ├── tests/
│   │   ├── __tests__/
│   │   │   ├── components/
│   │   │   └── pages/
│   │   └── setup.ts                  # Test setup
│   ├── node_modules/                 # Node.js dependencies
│   ├── package.json
│   ├── package-lock.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── eslint.config.js
│
├── docker/                           # Docker configuration
│   ├── Dockerfile                    # Multi-stage build
│   ├── Dockerfile.dev                # Development image
│   └── docker-compose.dev.yml        # Local development
│
├── scripts/                          # Build & deployment scripts
│   ├── setup.sh                      # Initial project setup
│   ├── dev.sh                        # Development startup
│   ├── backend.sh                    # Backend only
│   ├── frontend.sh                   # Frontend only
│   ├── build.sh                      # Production build
│   ├── test.sh                       # Run tests
│   ├── clean.sh                      # Clean artifacts
│   └── deploy.sh                     # CapRover deployment
│
├── docs/                             # Documentation
│   ├── PROJECT_STRUCTURE.md          # This file
│   ├── API_DOCUMENTATION.md          # API documentation
│   └── DEPLOYMENT_GUIDE.md           # CapRover deployment guide
│
├── voices/                           # Legacy voice models location
├── venv/                             # Legacy virtual environment
├── tts.py                           # Legacy command-line script
├── captain-definition                # CapRover configuration
├── .gitignore                        # Global gitignore
├── .env                              # Environment variables (local)
├── .env.example                      # Environment variables template
├── Makefile                          # Development commands
└── README.md                         # Project overview
```

## 🗂️ Legacy and Migration

```
# Legacy files (still functional)
tts.py                                # Original command-line script
voices/                               # Old voice models location
venv/                                 # Old virtual environment location

# Migration artifacts
.deps_installed                       # Dependency installation marker
__pycache__/                          # Python bytecode cache (ignored)
*.pyc                                 # Python compiled files (ignored)
.pytest_cache/                        # Pytest cache (ignored)
```

## 📊 File Types and Extensions

### Python Files

- `.py` - Python source code
- `.pyc` - Python bytecode (ignored)
- `__pycache__/` - Python cache directories (ignored)

### TypeScript/JavaScript Files

- `.ts` - TypeScript source code
- `.tsx` - TypeScript JSX components
- `.js` - JavaScript files
- `.mjs` - ES modules JavaScript
- `.json` - JSON configuration files

### Configuration Files

- `requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies
- `Makefile` - Build automation
- `.env` - Environment variables
- `tsconfig.json` - TypeScript configuration
- `tailwind.config.js` - TailwindCSS configuration

### Audio and Model Files

- `.onnx` - ONNX neural network models
- `.wav` - WAV audio files
- `.mp3` - MP3 audio files (future)
- `.pdf` - PDF documents (input)
- `.epub` - EPUB documents (input)

## 🔄 Data Flow

```
1. File Upload (Frontend)
   └── src/components/FileUpload.tsx
       └── src/lib/api.ts
           └── POST /api/upload/file

2. Text Extraction (Backend)
   └── app/api/routes/upload.py
       └── app/services/text_extractor.py
           └── PyPDF2 / ebooklib

3. Text Processing (Backend)
   └── app/services/text_processor.py
       └── Unicode normalization
       └── Text chunking

4. TTS Conversion (Backend)
   └── app/services/tts_engine.py
       └── Piper TTS CLI
           └── voices/*.onnx

5. Audio Processing (Backend)
   └── app/services/audio_processor.py
       └── WAV concatenation
           └── storage/outputs/

6. Audio Delivery (Backend)
   └── app/api/routes/audio.py
       └── File serving
           └── Frontend audio player
```

## 🎯 Development Workflow

### 1. Setup Phase

```bash
make setup          # Run scripts/setup.sh
├── Backend setup   # Create venv, install dependencies
├── Frontend setup  # npm install
└── Environment     # Create .env file
```

### 2. Development Phase

```bash
make dev           # Run scripts/dev.sh
├── Backend start  # uvicorn app.main:app --reload
├── Frontend start # npm run dev
└── Watch mode     # Auto-reload on changes
```

### 3. Testing Phase

```bash
make test          # Run scripts/test.sh
├── Backend tests  # pytest tests/
├── Frontend tests # npm test (future)
└── Integration    # Full workflow tests
```

### 4. Build Phase

```bash
make build         # Run scripts/build.sh
├── Frontend build # npm run build
├── Backend check  # Import validation
└── Docker image   # Production container
```

This structure provides clear separation of concerns, scalability, and maintainability for the Audio Book Converter application.
