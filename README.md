# Audio Book Converter

Convert PDF and EPUB documents to high-quality audio books using AI-powered text-to-speech technology with Piper TTS.

## 🚀 Quick Start

### One-time Setup

```bash
# Clone and setup the project
git clone <repo-url>
cd audio-book

# Initial setup (creates venv, installs dependencies)
make setup
```

### Development

```bash
# Start both backend and frontend
make dev

# Or start individually
make backend    # Python FastAPI server (port 8000)
make frontend   # Next.js app (port 3000)
```

### Production Deployment

```bash
# Build and deploy to CapRover
make build
make deploy
```

## 🏗️ Architecture

- **Backend**: Python FastAPI with Piper TTS engine
- **Frontend**: Next.js 15 with TypeScript and TailwindCSS
- **Deployment**: Docker multi-stage build + CapRover
- **Storage**: Local file system (uploads + generated audio)
- **TTS Engine**: Piper (offline neural text-to-speech)

## 📁 Project Structure

```
audio-book/
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── main.py                   # FastAPI application entry point
│   │   ├── api/routes/               # API endpoints (upload, convert, audio)
│   │   ├── services/                 # Business logic (TTS, text processing)
│   │   ├── models/                   # Pydantic schemas and enums
│   │   └── core/                     # Configuration and exceptions
│   ├── tests/                        # Backend tests (unit + integration)
│   ├── voices/                       # TTS voice models (.onnx files)
│   ├── storage/                      # File storage (uploads + outputs)
│   ├── venv/                         # Python virtual environment
│   ├── requirements.txt              # Production dependencies
│   └── requirements-dev.txt          # Development dependencies
├── frontend/                         # Next.js frontend
│   ├── src/
│   │   ├── app/                      # Next.js App Router pages
│   │   ├── components/               # React components
│   │   ├── lib/                      # API client and utilities
│   │   └── hooks/                    # Custom React hooks (future)
│   ├── node_modules/                 # Node.js dependencies
│   └── package.json                  # Node.js dependencies
├── scripts/                          # Development and build scripts
│   ├── dev.sh                        # Start development servers
│   ├── setup.sh                      # Initial project setup
│   ├── backend.sh                    # Start backend only
│   ├── frontend.sh                   # Start frontend only
│   ├── build.sh                      # Production build
│   ├── test.sh                       # Run all tests
│   └── clean.sh                      # Clean build artifacts
├── docker/                           # Docker configuration (future)
├── docs/                             # Documentation
├── voices/                           # TTS voice models (legacy location)
├── venv/                             # Legacy virtual environment
├── Makefile                          # Development commands
├── .env                              # Environment variables
├── .gitignore                        # Git ignore rules
└── README.md                         # This file
```

## 🔧 Development

### Prerequisites

- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **Piper TTS binary** installed in PATH
- **Docker** (optional, for production builds)

### Installation

The setup script handles everything automatically:

```bash
# Automated setup
make setup
```

**Manual setup** (if needed):

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Frontend
cd frontend
npm install

# Install Piper TTS
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz
tar -xzf piper_amd64.tar.gz
sudo mv piper /usr/local/bin/
```

### Available Commands

| Command         | Script                  | Description             |
| --------------- | ----------------------- | ----------------------- |
| `make setup`    | `./scripts/setup.sh`    | Initial project setup   |
| `make dev`      | `./scripts/dev.sh`      | Start both servers      |
| `make backend`  | `./scripts/backend.sh`  | Start backend only      |
| `make frontend` | `./scripts/frontend.sh` | Start frontend only     |
| `make test`     | `./scripts/test.sh`     | Run all tests           |
| `make build`    | `./scripts/build.sh`    | Build for production    |
| `make clean`    | `./scripts/clean.sh`    | Clean build artifacts   |
| `make help`     | -                       | Show available commands |

### Daily Development Workflow

```bash
# Start development
make dev

# Access applications
# Backend API: http://localhost:8000
# Frontend:    http://localhost:3000
# API Docs:    http://localhost:8000/docs

# Stop servers: Ctrl+C
```

## 🎯 Features

### Current Features

- ✅ PDF and EPUB text extraction
- ✅ Text cleaning and preprocessing
- ✅ High-quality neural TTS with Piper
- ✅ Audio file generation (WAV format)
- ✅ Command-line interface (`tts.py`)
- ✅ Development environment setup

### Planned Features (Web App)

- 🔄 Web file upload interface
- 🔄 Real-time conversion progress
- 🔄 Audio player with controls
- 🔄 Multiple voice models support
- 🔄 Batch processing
- 🔄 Audio format conversion (MP3, etc.)
- 🔄 User settings and preferences

## 🧪 Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test

# Watch mode
npm test -- --watch
```

### Integration Tests

```bash
# Full application test
make test
```

## 🐳 Docker (Production)

### Build Production Image

```bash
# Build Docker image
docker build -f docker/Dockerfile -t audio-book-app .

# Run container
docker run -p 8000:8000 -v ./storage:/app/storage audio-book-app
```

### CapRover Deployment

1. **Create app in CapRover dashboard**

   - App name: `audio-book-app`
   - Enable HTTPS
   - Set custom domain (optional)

2. **Configure environment variables**

   ```bash
   DEBUG=false
   VOICE_MODEL=voices/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx
   LENGTH_SCALE=1.0
   NOISE_SCALE=0.667
   ```

3. **Deploy**
   ```bash
   make build
   caprover deploy --caproverUrl https://captain.your-domain.com \
                   --appName audio-book-app \
                   --tarFile build/audio-book-app.tar.gz
   ```

## 📖 API Documentation

- **Development**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Key Endpoints (Planned)

| Method | Endpoint                       | Description              |
| ------ | ------------------------------ | ------------------------ |
| POST   | `/api/upload/file`             | Upload PDF/EPUB file     |
| POST   | `/api/convert/start`           | Start TTS conversion     |
| GET    | `/api/convert/status/{job_id}` | Get conversion status    |
| GET    | `/api/audio/{job_id}`          | Download generated audio |
| GET    | `/health`                      | Health check             |

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Application
DEBUG=false
APP_NAME="TTS Audio Book Converter"

# TTS Configuration
VOICE_MODEL=voices/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx
LENGTH_SCALE=1.0              # Speech speed (0.9=faster, 1.1=slower)
NOISE_SCALE=0.667             # Voice variation
SENTENCE_SILENCE=0.35         # Pause between sentences
PAUSE_BETWEEN_BLOCKS=0.35     # Pause between text blocks

# File Processing
MAX_FILE_SIZE=52428800        # 50MB upload limit
MAX_CHUNK_CHARS=1500          # Text chunk size for processing

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Production (CapRover)
CAPROVER_URL=https://captain.your-domain.com
APP_NAME=audio-book-app
```

### Voice Models

The application uses Piper TTS voice models. Default model:

- **Language**: French (fr_FR)
- **Voice**: Siwis (female voice)
- **Quality**: Low (faster processing)
- **Files**: `fr_FR-siwis-low.onnx` + `fr_FR-siwis-low.onnx.json`

Additional voice models can be downloaded from [Piper TTS releases](https://github.com/rhasspy/piper/releases/).

## 🔍 Troubleshooting

### Common Issues

**1. Piper TTS not found**

```bash
# Check installation
which piper

# Install if missing
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz
tar -xzf piper_amd64.tar.gz
sudo mv piper /usr/local/bin/
```

**2. Voice model not found**

```bash
# Check voice models location
ls -la backend/voices/fr/fr_FR/siwis/low/
# Should contain: fr_FR-siwis-low.onnx and fr_FR-siwis-low.onnx.json
```

**3. Python virtual environment issues**

```bash
# Recreate virtual environment
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**4. Node.js dependency conflicts**

```bash
# Clean npm cache
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**5. Port already in use**

```bash
# Kill processes on ports 8000/3000
sudo lsof -t -i:8000 | xargs kill -9
sudo lsof -t -i:3000 | xargs kill -9
```

### Performance Tips

- **Large files**: Files > 10MB may take several minutes to process
- **Memory usage**: Text processing keeps full content in memory
- **Storage**: Generated audio files are kept indefinitely (manual cleanup)
- **Concurrent processing**: Limited by CPU cores

## 📊 Monitoring

### Health Checks

- **Backend**: http://localhost:8000/health
- **Frontend**: http://localhost:3000 (homepage load)

### Logs

```bash
# Development logs (stdout)
make dev

# Production logs (if using Docker)
docker logs audio-book-app
```

## 🔒 Security

### File Upload Security

- File type validation (PDF/EPUB only)
- File size limits (50MB max)
- Sanitized file names
- Isolated processing environment

### Production Security

- No debug mode in production
- HTTPS enforced via CapRover
- Environment variables for configuration
- No sensitive data in logs

## 🛠️ Development Workflow

### Adding New Features

1. **Backend changes** (Python):

   ```bash
   cd backend
   source venv/bin/activate
   # Edit code in app/
   # Add tests in tests/
   python -m pytest tests/
   ```

2. **Frontend changes** (TypeScript):

   ```bash
   cd frontend
   # Edit code in src/
   npm run type-check
   npm run lint
   ```

3. **Test integration**:
   ```bash
   make dev  # Test locally
   make test # Run all tests
   ```

### Code Quality

```bash
# Lint and format
cd backend && ruff check . && ruff format .
cd frontend && npm run lint

# Type checking
cd backend && mypy app/
cd frontend && npm run type-check
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and test
make test

# Commit with conventional format
git commit -m "feat: add amazing feature"

# Push and create PR
git push origin feature/amazing-feature
```

## 📝 Migration Notes

This project evolved from a standalone Python script (`tts.py`) to a full-stack web application:

### Legacy Files

- `tts.py` - Original command-line script (still functional)
- `voices/` - Voice models (moved to `backend/voices/`)
- `venv/` - Old virtual environment (moved to `backend/venv/`)

### Current Architecture

- **Monorepo structure** with separate backend/frontend
- **FastAPI backend** with modular services
- **Next.js frontend** with TypeScript
- **Automated development** with scripts and Makefile

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Piper TTS](https://github.com/rhasspy/piper) - High-quality neural text-to-speech
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React framework for production
- [CapRover](https://caprover.com/) - Free and open source PaaS

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ThibaultG94/audio-book/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ThibaultG94/audio-book/discussions)
- **Documentation**: [Project Wiki](https://github.com/ThibaultG94/audio-book/wiki)

---

Made with ❤️ for converting books to audio using AI
