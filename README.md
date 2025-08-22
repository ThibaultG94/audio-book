# Audio Book Converter

Convert PDF and EPUB documents to high-quality audio books using AI-powered text-to-speech technology.

## 🚀 Quick Start

### Development Setup

```bash
# Clone and navigate to project
git clone <repo-url>
cd audio-book-app

# Start development servers
make dev
```

### Production Deployment (CapRover)

```bash
# Build and deploy to CapRover
make deploy
```

## 🏗️ Architecture

- **Backend**: Python FastAPI with Piper TTS engine
- **Frontend**: Next.js with TypeScript and TailwindCSS
- **Deployment**: Docker multi-stage build + CapRover
- **Storage**: Local file system (uploads + generated audio)

## 📁 Project Structure

```
audio-book-app/
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── main.py                   # FastAPI app entry point
│   │   ├── api/routes/               # API endpoints (upload, convert, audio)
│   │   ├── services/                 # Business logic (TTS, text processing)
│   │   ├── models/                   # Pydantic schemas and enums
│   │   └── core/                     # Configuration and exceptions
│   ├── tests/                        # Backend tests (unit + integration)
│   ├── voices/                       # TTS voice models (.onnx files)
│   ├── storage/                      # File storage (uploads + outputs)
│   └── requirements.txt              # Python dependencies
├── frontend/                         # Next.js frontend
│   ├── src/
│   │   ├── app/                      # Next.js App Router pages
│   │   ├── components/               # React components
│   │   ├── lib/                      # API client and utilities
│   │   └── hooks/                    # Custom React hooks
│   └── package.json                  # Node.js dependencies
├── docker/                           # Docker configuration
├── scripts/                          # Build and deployment scripts
└── docs/                             # Documentation
```

## 🔧 Development

### Prerequisites

- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **Piper TTS binary** installed in PATH
- **Docker** (for production builds)

### Installation

#### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install Piper TTS (if not already installed)
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz
tar -xzf piper_amd64.tar.gz
sudo mv piper /usr/local/bin/
```

#### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Install testing dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event
npm install --save-dev @types/jest jest jest-environment-jsdom
```

### Available Commands

| Command           | Description                                    |
| ----------------- | ---------------------------------------------- |
| `make dev`        | Start development servers (backend + frontend) |
| `make test`       | Run all tests (backend + frontend)             |
| `make lint`       | Lint and format code                           |
| `make type-check` | Run type checking                              |
| `make build`      | Build for production                           |
| `make deploy`     | Deploy to CapRover                             |
| `make clean`      | Clean build artifacts                          |

### Manual Development

#### Backend (Port 8000)

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend (Port 3000)

```bash
cd frontend
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

## 🐳 Docker

### Development

```bash
# Start with Docker Compose
docker-compose -f docker/docker-compose.dev.yml up
```

### Production Build

```bash
# Build production image
docker build -f docker/Dockerfile -t audio-book-app .

# Run production container
docker run -p 8000:8000 -v ./storage:/app/storage audio-book-app
```

## 🚀 Deployment

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
   # Automated deployment
   make deploy

   # Or manual deployment
   ./scripts/build.sh
   caprover deploy --caproverUrl https://captain.your-domain.com \
                   --appName audio-book-app \
                   --tarFile build/audio-book-app.tar.gz
   ```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Application
DEBUG=false
APP_NAME="TTS Audio Book Converter"

# TTS Configuration
VOICE_MODEL=voices/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx
LENGTH_SCALE=1.0
NOISE_SCALE=0.667
SENTENCE_SILENCE=0.35
PAUSE_BETWEEN_BLOCKS=0.35

# File Processing
MAX_FILE_SIZE=52428800  # 50MB
MAX_CHUNK_CHARS=1500

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Production (CapRover)
CAPROVER_URL=https://captain.your-domain.com
APP_NAME=audio-book-app
```

## 📖 API Documentation

- **Development**: http://localhost:8000/docs
- **Production**: https://your-app.com/docs

### Key Endpoints

| Method | Endpoint                       | Description              |
| ------ | ------------------------------ | ------------------------ |
| POST   | `/api/upload/file`             | Upload PDF/EPUB file     |
| POST   | `/api/convert/start`           | Start TTS conversion     |
| GET    | `/api/convert/status/{job_id}` | Get conversion status    |
| GET    | `/api/audio/{job_id}`          | Download generated audio |

## 🧪 Testing

### Backend Tests

```bash
cd backend
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

# Coverage
npm test -- --coverage
```

### Integration Tests

```bash
# Full application test
make test
```

## 🔍 Troubleshooting

### Common Issues

**1. Piper TTS not found**

```bash
# Check if Piper is installed
which piper

# If not found, install:
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz
tar -xzf piper_amd64.tar.gz
sudo mv piper /usr/local/bin/
```

**2. Voice model not found**

```bash
# Ensure voice models are in the correct directory
ls -la backend/voices/fr/fr_FR/siwis/low/
# Should contain: fr_FR-siwis-low.onnx and fr_FR-siwis-low.onnx.json
```

**3. Frontend TypeScript errors**

```bash
# Install missing test dependencies
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom @types/jest
```

**4. Docker build fails**

```bash
# Clean Docker cache
docker system prune -a

# Rebuild
docker build -f docker/Dockerfile -t audio-book-app . --no-cache
```

### Performance Tips

- **Large files**: Files > 10MB may take several minutes to process
- **Concurrent conversions**: Limited by CPU cores (default: 2 simultaneous jobs)
- **Storage cleanup**: Generated files are kept for 24h (configurable)

## 🛠️ Development Workflow

### Adding New Features

1. **Backend changes**:

   ```bash
   cd backend
   # Add service/route/model
   # Add tests
   python -m pytest tests/
   ```

2. **Frontend changes**:

   ```bash
   cd frontend
   # Add component/hook/page
   # Add tests
   npm test
   ```

3. **Integration**:
   ```bash
   make dev  # Test locally
   make build  # Test production build
   ```

### Code Quality

```bash
# Lint all code
make lint

# Type checking
make type-check

# Format code
cd backend && ruff format .
cd frontend && npm run format
```

## 📊 Monitoring

### Logs

```bash
# Backend logs
tail -f backend/app.log

# Docker logs
docker logs -f audio-book-app
```

### Health Checks

- **Backend**: http://localhost:8000/health
- **Frontend**: http://localhost:3000 (should load homepage)

## 🔒 Security

### File Upload Security

- File type validation (PDF/EPUB only)
- Size limits (50MB max)
- Sanitized file names
- Isolated processing environment

### Production Security

- No debug mode in production
- HTTPS enforced via CapRover
- Environment variables for secrets
- File cleanup after processing

## 📝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Run quality checks: `make lint && make test`
5. Commit: `git commit -m 'feat: add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Create Pull Request

### Commit Convention

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Piper TTS](https://github.com/rhasspy/piper) - High-quality neural text-to-speech
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React framework for production
- [CapRover](https://caprover.com/) - Free and open source PaaS

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/audio-book-app/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/audio-book-app/discussions)
- **Documentation**: [Project Wiki](https://github.com/your-repo/audio-book-app/wiki)

---

Made with ❤️ for converting books to audio
