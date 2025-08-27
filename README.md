# 🎧 Audio Book Converter

Convert PDF and EPUB documents to high-quality audiobooks using AI-powered text-to-speech technology with Piper TTS. Modern web application with FastAPI backend and Next.js frontend.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with pip
- Node.js 18+ with npm
- Piper TTS installed (`pip install piper-tts`)

### Development Setup

```bash
# 1. Backend (FastAPI) - Port 8001
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# 2. Frontend (Next.js) - Port 3001  
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8001" > .env.local
npm run dev
```

### Access the Application
- **Frontend**: http://localhost:3001 (main application)
- **Backend API**: http://localhost:8001 (REST API)
- **API Documentation**: http://localhost:8001/docs (if DEBUG=True)

## ✨ Features

### 🎤 Advanced Voice System
- **7 French TTS Voices** with quality levels (Siwis, Tom, Gilles, MLS, UPMC...)
- **Voice Recommendations** based on usage (audiobook, news, storytelling)
- **Real-time Voice Preview** with custom text testing
- **Advanced Parameters**: speed, expressiveness, phonetic variation, sentence pauses
- **Smart Presets**: audiobook natural, news fast, storytelling expressive

### 📚 Document Processing  
- **PDF Support** with text extraction and structure preservation
- **EPUB Support** for native ebook processing
- **File Validation** with drag & drop interface
- **Progress Tracking** with visual step indicators
- **Error Handling** with detailed user feedback

### 🎨 Modern UI/UX
- **Responsive Design** with Tailwind CSS gradients
- **Interactive Components** with smooth animations
- **Real-time Feedback** for all user actions
- **Accessibility Features** with keyboard navigation
- **Mobile Optimized** for all screen sizes

### ⚡ Backend Performance
- **FastAPI Framework** with async processing
- **Chunked Processing** for optimal audio generation
- **Comprehensive API** with full error handling
- **File Management** with automatic cleanup
- **Extensible Architecture** for future enhancements

## 🏗️ Architecture

### Tech Stack
- **Backend**: Python FastAPI + Pydantic + Piper TTS
- **Frontend**: Next.js 15 + TypeScript + Tailwind CSS
- **Audio Engine**: Piper TTS (offline neural text-to-speech)
- **Storage**: Local filesystem with organized structure
- **Development**: Hot reload, TypeScript strict mode

### Key Components

```
audio-book-converter/
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── main.py                   # FastAPI application entry point
│   │   ├── api/routes/               # API endpoints
│   │   │   ├── voice.py              # Voice management
│   │   │   ├── preview.py            # TTS previews
│   │   │   ├── upload.py             # File uploads
│   │   │   ├── convert.py            # Main conversion
│   │   │   └── audio.py              # Audio serving
│   │   ├── services/                 # Business logic
│   │   │   ├── tts_engine.py         # Core TTS engine
│   │   │   ├── preview_tts.py        # Preview service
│   │   │   ├── text_processor.py     # Text processing
│   │   │   └── audio_processor.py    # Audio post-processing
│   │   ├── models/                   # Pydantic schemas
│   │   │   └── voice.py              # Voice models
│   │   └── core/                     # Configuration & exceptions
│   ├── voices/                       # TTS voice models (.onnx files)
│   └── storage/                      # File storage (uploads + outputs)
└── frontend/                         # Next.js frontend
    ├── src/
    │   ├── app/                      # Next.js App Router
    │   │   ├── page.tsx              # Main page
    │   │   └── convert/[id]/         # Conversion status page
    │   ├── components/               # React components
    │   │   ├── VoiceSelector.tsx     # Advanced voice selection
    │   │   ├── VoicePreview.tsx      # Voice preview interface
    │   │   ├── FileUpload.tsx        # Drag & drop upload
    │   │   └── ConversionStatus.tsx  # Progress tracking
    │   └── lib/                      # API client and types
    │       ├── api.ts                # HTTP client with error handling
    │       └── types.ts              # TypeScript definitions
    └── public/                       # Static assets
```

## 🔧 API Endpoints

### Voice Management
- `GET /api/voice/list` - Complete voice list with metadata
- `GET /api/preview/voices` - Voices with recommendations
- `GET /api/voice/{voice_id}` - Detailed voice information
- `POST /api/preview/tts` - Generate voice preview
- `GET /api/preview/parameters/defaults` - Default TTS parameters

### File Processing
- `POST /api/upload/file` - Upload PDF/EPUB document
- `POST /api/convert/start` - Start conversion job
- `GET /api/convert/status/{job_id}` - Get conversion progress

### Audio Serving
- `GET /api/audio/{job_id}` - Stream audio file
- `GET /api/audio/{job_id}/download` - Download audio file
- `GET /api/preview/audio/{preview_id}` - Preview audio file

### Utility
- `GET /health` - Service health check
- `POST /api/preview/cleanup` - Clean old preview files

## 🎛️ Configuration

### Backend Configuration (`backend/app/core/config.py`)

```python
# TTS Settings
DEFAULT_VOICE_MODEL = "fr_FR-siwis-low"
DEFAULT_LENGTH_SCALE = 1.0      # Speech speed (0.5-2.0)
DEFAULT_NOISE_SCALE = 0.667     # Expressiveness (0.0-1.0)
DEFAULT_NOISE_W = 0.8           # Phonetic variation (0.0-1.0)
DEFAULT_SENTENCE_SILENCE = 0.35 # Pause between sentences

# File Processing
MAX_FILE_SIZE = 52428800        # 50MB max file size
ALLOWED_EXTENSIONS = {".pdf", ".epub"}

# Storage Paths
STORAGE_BASE_PATH = Path("storage")
VOICES_BASE_PATH = Path("voices")
```

### Environment Variables

**Backend (`.env`)**:
```bash
DEBUG=true
APP_NAME="TTS Audio Book Converter"
HOST=0.0.0.0
PORT=8001
```

**Frontend (`.env.local`)**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8001
```

## 🎤 Voice Configuration

### Available Voices (7 French voices)

| Voice | Gender | Quality | Use Case | Size |
|-------|--------|---------|----------|------|
| `fr_FR-siwis-low` | Female | Low | Quick previews | ~60MB |
| `fr_FR-siwis-medium` | Female | Medium | Balanced quality | ~120MB |
| `fr_FR-mls-medium` | Female | Medium | Natural speech | ~150MB |
| `fr_FR-tom-medium` | Male | Medium | Storytelling | ~100MB |
| `fr_FR-gilles-low` | Male | Low | News/factual | ~60MB |
| `fr_FR-upmc-medium` | Neutral | Medium | Professional | ~130MB |
| `fr_FR-mls_1840-low` | Female | Low | Conversation | ~80MB |

### TTS Parameters

- **`length_scale`** (0.5-2.0): Speech speed control
- **`noise_scale`** (0.0-1.0): Expressiveness and emotion
- **`noise_w`** (0.0-1.0): Phonetic variation for naturalness  
- **`sentence_silence`** (0.0-2.0): Pause duration between sentences

### Voice Presets

- **📚 Audiobook Natural**: Optimized for long-form reading
- **📰 News Fast**: Quick, clear delivery for information
- **🎭 Storytelling Expressive**: Maximum emotion for narratives

## 🧪 Testing

### Manual Testing Workflow

1. **Voice Preview Test**:
   - Navigate to http://localhost:3001
   - Select different voices and adjust parameters
   - Generate previews with custom text
   - Verify audio playback works

2. **File Upload Test**:
   - Drag & drop a PDF/EPUB file
   - Verify file validation and progress
   - Check error handling for invalid files

3. **Conversion Test**:
   - Start a conversion with selected voice settings
   - Monitor progress on conversion status page
   - Verify final audio download

### API Testing

```bash
# Health check
curl http://localhost:8001/health

# List voices
curl http://localhost:8001/api/preview/voices

# Generate preview
curl -X POST "http://localhost:8001/api/preview/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test.",
    "voice_model": "fr_FR-siwis-low",
    "length_scale": 1.0,
    "noise_scale": 0.667
  }'
```

## 🛠️ Development

### Code Structure

**Backend (Python)**:
- **FastAPI** with async/await for performance
- **Pydantic v2** for data validation and serialization
- **Modular design** with clear separation of concerns
- **Comprehensive error handling** with custom exceptions
- **Type hints** throughout for better IDE support

**Frontend (TypeScript/React)**:
- **Next.js 15** with App Router for modern React patterns
- **TypeScript strict mode** for type safety
- **Custom hooks** for state management
- **Component composition** for reusability
- **Tailwind CSS** for consistent styling

### Development Workflow

1. **Start both servers** (backend on 8001, frontend on 3001)
2. **Make changes** with hot reload enabled
3. **Test functionality** manually and with API calls
4. **Verify types** compile correctly
5. **Check logs** for any errors

### Adding New Features

**New Voice Models**:
1. Place `.onnx` and `.onnx.json` files in `backend/voices/`
2. Restart backend to auto-detect
3. Test with voice preview interface

**New API Endpoints**:
1. Add route in `backend/app/api/routes/`
2. Update types in `frontend/src/lib/types.ts`
3. Add client method in `frontend/src/lib/api.ts`

## 🔍 Troubleshooting

### Common Issues

**"Backend non accessible"**:
- Verify backend is running on port 8001
- Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
- Ensure no firewall blocking the connection

**"Voice not found" errors**:
- Check voice files exist in `backend/voices/` directory
- Verify file permissions allow reading
- Restart backend after adding new voices

**"Import errors" in frontend**:
- Clear Next.js cache: `rm -rf frontend/.next`
- Reinstall dependencies: `cd frontend && npm install`
- Check TypeScript compilation: `npm run build`

**"Piper not found" errors**:
- Install Piper TTS: `pip install piper-tts`
- Verify installation: `which piper`
- Check PATH environment variable

### Debug Mode

**Backend debugging**:
```bash
cd backend
DEBUG=true python -m uvicorn app.main:app --reload --log-level debug
```

**Frontend debugging**:
```bash
cd frontend
npm run dev -- --inspect
```

### Health Checks

```bash
# Backend health
curl http://localhost:8001/health

# Voice availability
curl http://localhost:8001/api/preview/voices | jq '.count'

# Frontend accessibility
curl -I http://localhost:3001
```

## 📦 Deployment

### Production Considerations

- Set `DEBUG=false` in production
- Use proper HTTPS certificates
- Configure CORS for production domains
- Set up file storage with proper permissions
- Monitor disk space for audio files
- Configure log rotation

### Docker Deployment (Optional)

```dockerfile
# Multi-stage build combining backend and frontend
FROM python:3.11-slim as backend
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .

FROM node:18-alpine as frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM python:3.11-slim as production
WORKDIR /app
COPY --from=backend /app/backend .
COPY --from=frontend /app/frontend/out ./static
EXPOSE 8001
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

## 🎯 Current Status

### ✅ Fully Functional Features

- **Voice System**: 7 voices with preview and recommendations
- **File Processing**: PDF/EPUB upload with validation
- **TTS Engine**: Advanced parameter control with presets
- **UI/UX**: Modern responsive interface with animations
- **API**: Complete REST API with error handling
- **Progress Tracking**: Real-time conversion status
- **Audio Playback**: Integrated player with download

### 🚀 Performance Metrics

- **Voice Preview**: ~2-3 seconds generation time
- **File Upload**: Supports up to 50MB files
- **Conversion Speed**: ~1 minute per 1000 characters
- **Memory Usage**: ~200MB base + ~100MB per concurrent job
- **Storage Efficiency**: Automatic cleanup of temporary files

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Piper TTS](https://github.com/rhasspy/piper)** - High-quality neural text-to-speech engine
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[Next.js](https://nextjs.org/)** - React framework for production
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework

---

**Ready to use! Access your application at: http://localhost:3001**

*Powered by Piper TTS • AI-driven natural voice synthesis*