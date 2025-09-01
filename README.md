# 🎧 Audio Book Converter

Convert PDF and EPUB documents to high-quality audiobooks using AI-powered text-to-speech with Piper TTS. Modern web application with FastAPI backend and Next.js frontend.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ with pip
- Node.js 18+ with npm
- Piper TTS installed (`pip install piper-tts`)
- 2GB free disk space for voice models

### Installation

```bash
# Clone repository
git clone https://github.com/your-repo/audiobook-converter.git
cd audiobook-converter

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8001" > .env.local

# Download voice models (optional - basic voices included)
cd ../backend/voices
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx.json
```

### Running the Application

```bash
# Terminal 1 - Start backend
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2 - Start frontend
cd frontend
npm run dev -- --port 3001
```

Access the application:

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## ✨ Features

### 🎤 Advanced Voice System

- **7 French TTS Voices** with different quality levels (Siwis, Tom, Gilles, MLS, UPMC)
- **Visual Voice Selection** with prominent card-based interface
- **Real-time Voice Preview** with customizable parameters
- **Smart Recommendations** based on use case (audiobook, news, storytelling)
- **Advanced TTS Parameters**: speed, expressiveness, phonetic variation, pauses

### 📚 Document Processing

- **PDF Support** with intelligent text extraction
- **EPUB Support** for native ebook processing
- **Automatic Chapter Detection** and segmentation
- **Text Cleaning** with punctuation preservation
- **File Size Limit**: 50MB per document

### 🎯 Conversion Pipeline

- **Multi-step Process**: extraction → processing → synthesis → finalization
- **Real-time Progress Tracking** with visual indicators
- **Chapter-by-chapter Progress** display
- **Duration Estimation** for completed audiobooks
- **Error Recovery** with detailed error messages

### 🎨 Modern UI/UX

- **Responsive Design** with Tailwind CSS
- **Smooth Animations** and transitions
- **Drag & Drop** file upload
- **Accessibility** with keyboard navigation
- **Mobile Optimized** for all screen sizes

## 🏗️ Architecture

### Tech Stack

#### Backend (Port 8001)

- **Framework**: FastAPI with async/await support
- **TTS Engine**: Piper TTS for neural voice synthesis
- **Text Extraction**: PyPDF2 for PDFs, EbookLib for EPUBs
- **Audio Processing**: Wave, pydub for audio manipulation
- **Testing**: pytest with coverage reports

#### Frontend (Port 3001)

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript with strict mode
- **Styling**: Tailwind CSS with custom gradients
- **State Management**: React hooks (useState, useEffect)
- **API Client**: Custom client with error handling

### Project Structure

```
audiobook-converter/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry
│   │   ├── api/routes/             # API endpoints
│   │   │   ├── voice.py            # Voice management
│   │   │   ├── preview.py          # TTS preview
│   │   │   ├── upload.py           # File upload
│   │   │   ├── convert.py          # Conversion pipeline
│   │   │   └── audio.py            # Audio serving
│   │   ├── services/               # Business logic
│   │   │   ├── tts_engine.py       # Piper TTS integration
│   │   │   ├── text_extractor.py   # Document parsing
│   │   │   ├── text_processor.py   # Text cleaning
│   │   │   └── conversion_service.py # Conversion orchestration
│   │   ├── models/                 # Data models
│   │   └── core/                   # Configuration
│   ├── voices/                     # Voice model files
│   ├── storage/                    # File storage
│   └── tests/                      # Test suite
├── frontend/
│   ├── src/
│   │   ├── app/                    # Next.js pages
│   │   ├── components/             # React components
│   │   │   ├── VoiceSelector.tsx   # Voice selection UI
│   │   │   ├── VoicePreview.tsx    # Voice testing
│   │   │   ├── FileUpload.tsx      # File upload
│   │   │   └── ConversionStatus.tsx # Progress tracking
│   │   └── lib/                    # Utilities
│   │       ├── api.ts              # API client
│   │       └── types.ts            # TypeScript types
│   └── public/                     # Static assets
└── deployment/                     # Docker/CapRover configs
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)

```bash
# Application
DEBUG=true
APP_NAME="Audio Book Converter"
VERSION="1.0.0"

# Server
HOST=0.0.0.0
PORT=8001

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:3001"]

# TTS Configuration
DEFAULT_VOICE_MODEL=fr_FR-siwis-low
DEFAULT_LENGTH_SCALE=1.0
DEFAULT_NOISE_SCALE=0.667
DEFAULT_NOISE_W=0.8
DEFAULT_SENTENCE_SILENCE=0.35

# File Processing
MAX_FILE_SIZE=52428800  # 50MB
ALLOWED_EXTENSIONS=[".pdf", ".epub"]
```

#### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8001
```

### TTS Parameters

| Parameter          | Range   | Description                 |
| ------------------ | ------- | --------------------------- |
| `length_scale`     | 0.5-2.0 | Speech speed (1.0 = normal) |
| `noise_scale`      | 0.0-1.0 | Voice expressiveness        |
| `noise_w`          | 0.0-1.0 | Phonetic variation          |
| `sentence_silence` | 0.0-2.0 | Pause between sentences     |

## 📡 API Endpoints

### Voice Management

- `GET /api/voice/list` - List all available voices
- `GET /api/preview/voices` - Get voices with recommendations
- `POST /api/preview/tts` - Generate voice preview

### File Processing

- `POST /api/upload/file` - Upload PDF/EPUB file
- `POST /api/convert/start` - Start conversion job
- `GET /api/convert/status/{job_id}` - Get conversion progress
- `POST /api/convert/cancel/{job_id}` - Cancel conversion
- `GET /api/convert/list` - List all conversions

### Audio Serving

- `GET /api/audio/{job_id}` - Stream audio file
- `GET /api/audio/{job_id}/download` - Download audio file

## 🧪 Testing

### Run Tests

```bash
# Backend tests
cd backend
pytest                          # Run all tests
pytest --cov=app                # With coverage
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests only

# Frontend tests
cd frontend
npm test                        # Run test suite
npm run test:coverage           # With coverage
```

### Test Structure

```
backend/tests/
├── conftest.py                 # Shared fixtures
├── unit/                       # Unit tests
│   ├── test_conversion_service.py
│   ├── test_tts_engine.py
│   └── test_text_processor.py
└── integration/                # Integration tests
    ├── test_convert_api.py
    ├── test_voice_api.py
    └── test_upload_api.py
```

## 🚢 Deployment

### Docker

```bash
# Build image
docker build -t audiobook-converter:latest .

# Run container
docker run -d \
  -p 8001:8001 \
  -p 3001:3001 \
  -v $(pwd)/voices:/app/backend/voices \
  audiobook-converter:latest
```

### CapRover

1. Create `captain-definition` file:

```json
{
  "schemaVersion": 2,
  "dockerfilePath": "./Dockerfile"
}
```

2. Deploy:

```bash
caprover deploy
```

### Production Dockerfile

```dockerfile
# Backend build
FROM python:3.11-slim as backend
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .

# Frontend build
FROM node:18-alpine as frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production
COPY frontend/ .
RUN npm run build

# Production image
FROM python:3.11-slim
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy from build stages
COPY --from=backend /app/backend ./backend
COPY --from=frontend /app/frontend/.next ./frontend/.next
COPY --from=frontend /app/frontend/public ./frontend/public
COPY --from=frontend /app/frontend/package*.json ./frontend/

# Install Node.js for frontend
RUN apt-get update && apt-get install -y nodejs npm

# Create directories
RUN mkdir -p backend/storage/{uploads,outputs,temp} backend/voices

# Expose ports
EXPOSE 8001 3001

# Start script
COPY deployment/start.sh .
RUN chmod +x start.sh
CMD ["./start.sh"]
```

## 🔍 Troubleshooting

### Common Issues

#### Voice models not found

```bash
# Download French voices
cd backend/voices
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx.json
```

#### Piper TTS not installed

```bash
pip install piper-tts
# or download binary
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz
tar -xzf piper_amd64.tar.gz
sudo mv piper /usr/local/bin/
```

#### Frontend can't connect to backend

```bash
# Check backend is running
curl http://localhost:8001/health

# Verify environment variable
cat frontend/.env.local
# Should contain: NEXT_PUBLIC_API_URL=http://localhost:8001
```

#### CORS errors

Ensure backend CORS settings include frontend URL:

```python
# backend/app/core/config.py
ALLOWED_ORIGINS = ["http://localhost:3001"]
```

## 📊 Performance

### Benchmarks

- **Voice Preview**: ~2-3 seconds generation time
- **Text Extraction**: ~1 second per 100 pages
- **Audio Generation**: ~1 minute per 1000 characters
- **Memory Usage**: ~200MB base + 100MB per concurrent job
- **Max File Size**: 50MB (configurable)

### Optimization Tips

1. Use low-quality voices for faster processing
2. Implement caching for voice previews
3. Use job queue (Celery) for large conversions
4. Enable gzip compression in production
5. Use CDN for static assets

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'feat: add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Code style
- `refactor:` Code refactoring
- `test:` Tests
- `chore:` Maintenance

### Code Style

- **Python**: Black formatter, PEP8
- **TypeScript**: ESLint + Prettier
- **Tests**: Minimum 80% coverage

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- [Piper TTS](https://github.com/rhasspy/piper) - Neural text-to-speech engine
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React framework for production
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/audiobook-converter/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/audiobook-converter/discussions)
- **Documentation**: [Wiki](https://github.com/your-repo/audiobook-converter/wiki)

---

**Made with ❤️ by the AudioBook Converter Team**
