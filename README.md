# Audio Book Converter

Convert PDF and EPUB documents to high-quality audio books using AI-powered text-to-speech technology with Piper TTS.

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **Piper TTS binary** installed in PATH

### One-time Setup

```bash
# Clone and setup the project
git clone <repo-url>
cd audio-book

# Complete automated setup (creates venv, installs dependencies, voices)
make setup

# Or manual setup
./scripts/setup.sh
```

### Development

```bash
# Start both backend and frontend
make dev

# Or start individually
make backend    # Python FastAPI server (port 8000)
make frontend   # Next.js app (port 3000)
```

### Voice Installation

```bash
# Install balanced voice set (recommended)
./scripts/install-voices.sh default

# Install high-quality voices
./scripts/install-voices.sh premium

# Install single voice (fastest)
./scripts/install-voices.sh minimal
```

## 🏗️ Architecture

- **Backend**: Python FastAPI with advanced voice management system
- **Frontend**: Next.js 15 with TypeScript, TailwindCSS, and comprehensive voice selection UI
- **TTS Engine**: Piper (offline neural text-to-speech) with multiple voice support
- **Voice System**: Advanced voice metadata management, filtering, and recommendations
- **Testing**: Complete test suite with unit, integration, and API tests
- **Deployment**: Docker multi-stage build + CapRover

## 📁 Project Structure

```
audio-book/
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── main.py                   # FastAPI application entry point
│   │   ├── api/routes/               # API endpoints (upload, convert, audio, preview)
│   │   ├── services/                 # Business logic (TTS, voice management, processing)
│   │   ├── models/                   # Pydantic schemas and enums
│   │   └── core/                     # Configuration, exceptions, startup validation
│   ├── tests/                        # Complete test suite (unit + integration)
│   ├── voices/                       # TTS voice models with metadata system
│   └── storage/                      # File storage (uploads + outputs + previews)
├── frontend/                         # Next.js 15 TypeScript frontend
│   ├── src/
│   │   ├── app/                      # Next.js App Router pages
│   │   ├── components/               # React components (FileUpload, VoiceSelector, etc.)
│   │   └── lib/                      # API client and utilities
│   └── package.json                  # Node.js dependencies
├── scripts/                          # Development and deployment automation
│   ├── setup.sh                      # Complete project setup
│   ├── dev.sh                        # Start development servers
│   ├── install-voices.sh             # Automated voice installation
│   └── diagnosis.sh                  # System diagnostic and troubleshooting
├── docs/                             # Documentation
│   └── structure.md                  # Complete project structure reference
├── Makefile                          # Development commands
└── README.md                         # This file
```

## 🎯 Features

### Current Features

- ✅ **Advanced Voice Management**: Multiple voice models with metadata, filtering, and recommendations
- ✅ **Interactive Voice Preview**: Test voices with custom parameters before conversion
- ✅ **Intelligent Voice Selection**: Gender, quality, and usage-based filtering
- ✅ **PDF and EPUB text extraction** with enhanced French text preprocessing
- ✅ **High-quality neural TTS** with Piper and customizable parameters
- ✅ **Real-time conversion progress** with status polling
- ✅ **Comprehensive voice validation** and diagnostic tools
- ✅ **Automated voice installation** system
- ✅ **Complete test coverage** (unit + integration + API tests)

### Voice System Features

- 🎤 **Multi-Voice Support**: Female, male, and multi-speaker voices
- 🔧 **Advanced Parameters**: Speed, expressivity, pitch stability, sentence pauses
- 📊 **Voice Recommendations**: Usage-based suggestions (audiobook, news, storytelling)
- 🎛️ **Interactive Preview**: Test voices with custom text and parameters
- 📈 **Voice Analytics**: Statistics, validation, and performance metrics
- 🚀 **Easy Installation**: Automated download and setup of voice models

## 🔧 Available Commands

| Command         | Description             |
| --------------- | ----------------------- |
| `make setup`    | Initial project setup   |
| `make dev`      | Start both servers      |
| `make backend`  | Start backend only      |
| `make frontend` | Start frontend only     |
| `make test`     | Run all tests           |
| `make build`    | Build for production    |
| `make clean`    | Clean build artifacts   |
| `make help`     | Show available commands |

## 🎤 Voice Management

### Available Voice Models

- **Siwis** (Female): Low/Medium/High quality French voices
- **Tom** (Male): Warm and professional male voice
- **Bernard** (Male): Mature, authoritative voice for documentaries
- **UPMC** (Multi): Dual-speaker system (Jessica ♀ + Pierre ♂)

### Voice Installation Presets

```bash
# Balanced set (3 voices, ~180MB) - Recommended
./scripts/install-voices.sh default

# High quality (4 voices, ~340MB) - Premium experience
./scripts/install-voices.sh premium

# Single voice (~45MB) - Fastest setup
./scripts/install-voices.sh minimal

# All voices (~440MB) - Complete collection
./scripts/install-voices.sh all
```

### Voice System Commands

```bash
# List available voices
./scripts/install-voices.sh --list

# Test installed voices
./scripts/install-voices.sh --test

# System diagnostic
./scripts/diagnosis.sh

# Voice structure validation
./scripts/voices.sh
```

## 🔍 Development

### Daily Workflow

```bash
# Start development environment
make dev

# Access applications
# - Backend API: http://localhost:8000
# - Frontend: http://localhost:3000
# - API Documentation: http://localhost:8000/docs
# - Voice Preview API: http://localhost:8000/api/preview/voices

# Stop: Ctrl+C
```

### Testing

```bash
# Run all tests
make test

# Backend tests only
cd backend && python -m pytest tests/ -v

# Frontend tests only
cd frontend && npm test

# Integration tests
python -m pytest tests/integration/ -v
```

### Voice Development

```bash
# Voice system validation
curl http://localhost:8000/api/preview/voices

# Test voice parameters
curl http://localhost:8000/api/preview/parameters/defaults

# Voice installation guide
curl http://localhost:8000/api/preview/voices/install-guide
```

## 🐳 Production Deployment

### CapRover Deployment

1. **Build production image**:

   ```bash
   make build
   ```

2. **Deploy to CapRover**:

   ```bash
   # Configure environment variables in CapRover dashboard
   caprover deploy --caproverUrl https://captain.your-domain.com \
                   --appName audio-book-app
   ```

3. **Environment Variables**:
   ```bash
   DEBUG=false
   VOICE_MODEL=voices/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx
   LENGTH_SCALE=1.0
   NOISE_SCALE=0.667
   MAX_FILE_SIZE=52428800
   ```

## 🔒 Security Features

- File type validation (PDF/EPUB only)
- File size limits (50MB max)
- Sanitized file names with UUID-based storage
- Path traversal protection
- Environment-based configuration (no secrets in code)

## 📊 API Documentation

### Key Endpoints

| Method | Endpoint                           | Description              |
| ------ | ---------------------------------- | ------------------------ |
| POST   | `/api/upload/file`                 | Upload PDF/EPUB file     |
| POST   | `/api/convert/start`               | Start TTS conversion     |
| GET    | `/api/convert/status/{job_id}`     | Get conversion status    |
| GET    | `/api/audio/{job_id}`              | Download generated audio |
| GET    | `/api/preview/voices`              | List available voices    |
| POST   | `/api/preview/tts`                 | Generate voice preview   |
| GET    | `/api/preview/parameters/defaults` | Get TTS parameters       |

### Voice API Endpoints

- **Voice Management**: `/api/preview/voices` - Complete voice catalog with metadata
- **Voice Preview**: `/api/preview/tts` - Generate audio previews with custom parameters
- **Voice Validation**: `/api/preview/voices/validate` - Validate installed voices
- **Installation Guide**: `/api/preview/voices/install-guide` - Voice installation instructions

## 🧪 Quality Assurance

### Test Coverage

- **Unit Tests**: Services, utilities, and core components
- **Integration Tests**: Complete API workflows
- **Voice System Tests**: Voice management, validation, and preview generation
- **API Tests**: All endpoints with error handling

### Code Quality

- **Python**: PEP8, ruff formatting, mypy type checking
- **TypeScript**: ESLint, Prettier, strict TypeScript
- **Git Hooks**: Pre-commit linting and testing

## 🔧 Troubleshooting

### Common Issues

1. **Piper TTS not found**: Install with `./scripts/install-voices.sh`
2. **No voices available**: Run `./scripts/diagnosis.sh` for system check
3. **Backend connection error**: Verify FastAPI is running on port 8000
4. **Voice preview fails**: Check voice model paths and Piper installation

### Diagnostic Tools

```bash
# Complete system diagnostic
./scripts/diagnosis.sh

# Voice system specific check
./scripts/voices.sh

# Backend health check
curl http://localhost:8000/health

# Voice validation
curl http://localhost:8000/api/preview/voices/validate
```

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [Piper TTS](https://github.com/rhasspy/piper) - High-quality neural text-to-speech
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React framework for production
- [CapRover](https://caprover.com/) - Free and open source PaaS

---

**Made with ❤️ for converting books to audio using AI**
