# Audio Book Converter

Convert PDF and EPUB documents to high-quality audiobooks using AI-powered text-to-speech technology with Piper TTS.

## 🚀 Quick Start

### One-time Setup

```bash
# Clone and setup the project
git clone <repo-url>
cd audio-book-converter
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
audio-book-converter/
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── main.py                   # FastAPI application entry point
│   │   ├── api/routes/               # API endpoints (upload, convert, audio, preview)
│   │   ├── services/                 # Business logic (TTS, text processing, voice management)
│   │   ├── models/                   # Pydantic schemas and enums
│   │   └── core/                     # Configuration and exceptions
│   ├── tests/                        # Backend tests (unit + integration)
│   ├── voices/                       # TTS voice models (.onnx files)
│   ├── storage/                      # File storage (uploads + outputs)
│   └── requirements.txt              # Python dependencies
├── frontend/                         # Next.js frontend
│   ├── src/
│   │   ├── app/                      # Next.js App Router
│   │   ├── components/               # React components (upload, voice preview, audio player)
│   │   ├── lib/                      # API client and utilities
│   │   └── hooks/                    # Custom React hooks
│   ├── public/                       # Static assets
│   └── package.json                  # Node.js dependencies
├── scripts/                          # Development and deployment scripts
├── docs/                             # Project documentation
└── README.md                         # This file
```

For detailed project structure, see [docs/structure.md](docs/structure.md).

## ✨ Features

### Core Functionality

- **File Upload**: Drag & drop PDF/EPUB files with validation
- **Text Extraction**: Automatic content extraction from documents
- **Voice Selection**: Multiple TTS voices with quality levels
- **Voice Preview**: Test voices with custom text and parameters
- **Audio Generation**: High-quality speech synthesis
- **Real-time Progress**: Live conversion status updates
- **Audio Download**: Stream generated audiobook files

### Voice Management

- **Multi-language Support**: French, English, and more
- **Quality Levels**: Low (fast), Medium, High (best quality)
- **Voice Metadata**: Technical specs, usage recommendations
- **Preview System**: Test voices before full conversion
- **Parameter Tuning**: Speed, expressiveness, pauses

### Developer Experience

- **Hot Reload**: Automatic code refresh in development
- **Type Safety**: Full TypeScript integration
- **Error Handling**: Comprehensive error messages
- **Testing**: Unit, integration, and E2E tests
- **Documentation**: API docs with Swagger/OpenAPI

## 🔧 Configuration

### Environment Variables

#### Backend (.env)

```bash
DEBUG=true
APP_NAME="Audio Book Converter"

# TTS Configuration
DEFAULT_VOICE_MODEL=fr_FR-siwis-low
PIPER_EXECUTABLE=piper
MAX_FILE_SIZE=52428800  # 50MB

# Server
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=["http://localhost:3000"]
```

#### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### TTS Voice Configuration

The application uses Piper TTS voice models with the following structure:

```
backend/voices/
└── {language}/
    └── {locale}/
        └── {dataset}/
            └── {quality}/
                ├── {model}.onnx      # Neural network model
                └── {model}.onnx.json # Voice metadata
```

Default voice: French (fr_FR-siwis-low) - female voice, good for audiobooks.

## 🛠️ Development

### Available Commands

```bash
# Development
make setup      # Initial project setup
make dev        # Start development servers
make backend    # Backend only (FastAPI)
make frontend   # Frontend only (Next.js)

# Testing & Quality
make test       # Run all tests
make lint       # Code linting and formatting
make clean      # Clean build artifacts

# Production
make build      # Build Docker image
make deploy     # Deploy to CapRover
```

### Adding New Voices

1. Download voice models from [Piper releases](https://github.com/rhasspy/piper/releases)
2. Place in `backend/voices/{language}/{locale}/{dataset}/{quality}/`
3. Restart backend to auto-detect new voices

```bash
# Download additional voices
./scripts/download-voices.sh
```

### API Development

The backend exposes a RESTful API documented at `http://localhost:8000/docs` when running in development mode.

Key endpoints:

- `GET /api/preview/voices` - List available TTS voices
- `POST /api/preview/tts` - Generate voice preview
- `POST /api/upload/file` - Upload PDF/EPUB
- `POST /api/convert/start` - Start conversion job
- `GET /api/convert/status/{job_id}` - Get conversion progress
- `GET /api/audio/{job_id}` - Download generated audio

## 🧪 Testing

### Running Tests

```bash
# Backend tests (pytest)
cd backend
source venv/bin/activate
pytest tests/ -v --cov=app

# Frontend tests (Jest)
cd frontend
npm test -- --coverage

# Run all tests
make test
```

### Test Structure

- **Unit Tests**: Individual functions and components
- **Integration Tests**: API endpoints and workflows
- **E2E Tests**: Complete user workflows (optional)

Coverage targets: >80% for critical paths, >60% overall.

## 📦 Deployment

### Local Development

```bash
# Requirements
- Python 3.11+
- Node.js 18+
- Piper TTS binary

# Setup
make setup  # Installs everything automatically
make dev    # Start development environment
```

### Production (CapRover)

1. **Build the application**:

   ```bash
   make build
   ```

2. **Deploy to CapRover**:

   ```bash
   export CAPROVER_URL=https://captain.your-domain.com
   export APP_NAME=audio-book-converter
   make deploy
   ```

3. **Configure environment variables** in CapRover dashboard:
   - `DEBUG=false`
   - `DEFAULT_VOICE_MODEL=fr_FR-siwis-low`
   - `MAX_FILE_SIZE=52428800`

### Docker

```bash
# Build production image
docker build -t audio-book-converter .

# Run container
docker run -p 8000:8000 -v ./storage:/app/storage audio-book-converter
```

The Dockerfile uses multi-stage builds for optimization and includes both backend and frontend in a single container.

## 🔍 Troubleshooting

### Common Issues

**Backend not accessible**

- Check if port 8000 is available: `lsof -i :8000`
- Verify Piper TTS installation: `which piper`
- Check environment variables in `.env`

**Voices not loading**

- Ensure voice files are in `backend/voices/`
- Verify file permissions: `ls -la backend/voices/`
- Check logs for voice scanning errors

**Frontend build errors**

- Verify Node.js version: `node --version` (need 18+)
- Clear cache: `rm -rf frontend/.next frontend/node_modules`
- Reinstall: `cd frontend && npm install`

**CORS errors**

- Check `ALLOWED_ORIGINS` in backend `.env`
- Verify frontend URL matches allowed origins

### Debug Mode

Enable detailed logging:

```bash
# Backend debug mode
cd backend
DEBUG=true python -m uvicorn app.main:app --reload --log-level debug

# Frontend debug mode
cd frontend
npm run dev -- --inspect
```

### Health Checks

```bash
# Check backend health
curl http://localhost:8000/health

# Check available voices
curl http://localhost:8000/api/preview/voices
```

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes and test**: `make test`
4. **Commit with conventional format**: `git commit -m "feat: add amazing feature"`
5. **Push and create PR**: `git push origin feature/amazing-feature`

### Code Standards

- **Python**: PEP8, Black formatting, mypy type checking, pytest testing
- **TypeScript**: ESLint, Prettier, strict mode, Jest testing
- **Commits**: Conventional Commits format
- **Documentation**: Update README and API docs for changes

### Architecture Decisions

For major changes, create an Architecture Decision Record (ADR) in `docs/decisions/`.

## 📈 Roadmap

### Current Version (v1.0)

- ✅ Basic PDF/EPUB to audio conversion
- ✅ Voice preview system
- ✅ Multiple voice models
- ✅ Real-time progress tracking
- ✅ Web interface

### Planned Features (v2.0)

- 🔜 User authentication and accounts
- 🔜 Conversion history and library
- 🔜 Advanced audio processing (chapters, bookmarks)
- 🔜 Batch processing
- 🔜 Cloud voice models
- 🔜 Mobile responsive improvements

### Future Considerations

- Multi-tenant architecture
- Background job queuing (Redis/Celery)
- CDN integration for audio delivery
- Advanced AI features (summarization, etc.)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Piper TTS](https://github.com/rhasspy/piper) - High-quality neural text-to-speech
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React framework for production
- [CapRover](https://caprover.com/) - Free and open source PaaS

## 📞 Support

- **Documentation**: [Project Wiki](https://github.com/your-username/audio-book-converter/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-username/audio-book-converter/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/audio-book-converter/discussions)

---

Made with ❤️ for converting books to audio using AI
