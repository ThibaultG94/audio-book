# 🎛️ Audio Book Converter - Backend

FastAPI backend for converting PDF/EPUB documents to audiobooks using Piper TTS. Provides REST API for voice management, file processing, and audio generation.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Piper TTS (`pip install piper-tts`)
- Voice models (automatically detected in `voices/` directory)

### Development Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Access Points
- **API Server**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs (if DEBUG=True)
- **Health Check**: http://localhost:8001/health

## 🏗️ Architecture

### Project Structure

```
backend/
├── app/
│   ├── main.py                   # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/               # API route modules
│   │       ├── __init__.py
│   │       ├── voice.py          # Voice management endpoints
│   │       ├── preview.py        # TTS preview functionality
│   │       ├── upload.py         # File upload handling
│   │       ├── convert.py        # Main conversion process
│   │       └── audio.py          # Audio file serving
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # Application configuration
│   │   ├── exceptions.py         # Custom exception classes
│   │   └── startup_checks.py     # Application startup validation
│   ├── models/
│   │   ├── __init__.py
│   │   └── voice.py              # Pydantic models for voices
│   └── services/
│       ├── __init__.py
│       ├── tts_engine.py         # Core TTS engine (async)
│       ├── preview_tts.py        # Preview TTS service (sync)
│       ├── text_extractor.py     # PDF/EPUB text extraction
│       ├── text_processor.py     # Text cleaning and chunking
│       └── audio_processor.py    # Audio post-processing
├── voices/                       # TTS voice models (.onnx files)
├── storage/                      # File storage directory
│   ├── uploads/                  # Uploaded files
│   ├── outputs/                  # Generated audio files
│   └── temp/                     # Temporary files
├── tests/                        # Unit and integration tests
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

### Core Components

1. **FastAPI Application** (`app/main.py`)
   - CORS configuration for frontend integration
   - Exception handlers for graceful error responses
   - Static file serving for generated audio
   - Startup checks for voice models and directories

2. **API Routes** (`app/api/routes/`)
   - RESTful endpoints with proper HTTP status codes
   - Pydantic validation for request/response models
   - Comprehensive error handling with user-friendly messages

3. **Business Logic** (`app/services/`)
   - Modular service architecture
   - Separation of concerns between different operations
   - Async operations where appropriate for performance

4. **Configuration** (`app/core/config.py`)
   - Centralized settings with environment variable support
   - Pydantic BaseSettings for validation
   - Path management for storage and voice directories

## 🔧 API Reference

### Voice Management

#### List All Voices
```http
GET /api/voice/list
```
Returns complete voice inventory with metadata and technical information.

**Response:**
```json
{
  "voices": [
    {
      "id": "fr_FR-siwis-low",
      "model_path": "/path/to/model.onnx",
      "config_path": "/path/to/model.onnx.json",
      "metadata": {
        "name": "Siwis (Low Quality)",
        "language_code": "fr_FR",
        "gender": "female",
        "recommended_usage": ["audiobook", "storytelling"]
      },
      "technical_info": {
        "sample_rate": 16000,
        "num_speakers": 1,
        "model_size": "low"
      },
      "available": true
    }
  ],
  "count": 7,
  "default_voice": "fr_FR-siwis-low"
}
```

#### Get Voice Details
```http
GET /api/voice/{voice_id}
```
Retrieve detailed information about a specific voice model.

#### Validate Voice
```http
GET /api/voice/validate/{voice_id}
```
Check if a voice model is properly installed and usable.

### Preview System

#### List Preview Voices
```http
GET /api/preview/voices
```
Returns voices with usage recommendations and quality rankings.

**Response:**
```json
{
  "voices": [...],
  "count": 7,
  "default_voice": "fr_FR-siwis-low",
  "recommendations": {
    "fastest": "fr_FR-gilles-low",
    "highest_quality": "fr_FR-tom-medium",
    "most_natural": "fr_FR-siwis-medium",
    "french_best": "fr_FR-upmc-medium"
  }
}
```

#### Generate TTS Preview
```http
POST /api/preview/tts
Content-Type: application/json

{
  "text": "Sample text to synthesize",
  "voice_model": "fr_FR-siwis-low",
  "length_scale": 1.0,
  "noise_scale": 0.667,
  "noise_w": 0.8,
  "sentence_silence": 0.35
}
```

**Response:**
```json
{
  "preview_id": "uuid-string",
  "text": "Sample text to synthesize",
  "audio_url": "/api/preview/audio/uuid-string",
  "duration_estimate": 2.5,
  "voice_model": "fr_FR-siwis-low",
  "parameters": { ... }
}
```

#### Get Default Parameters
```http
GET /api/preview/parameters/defaults
```
Returns default TTS parameters with ranges and descriptions.

### File Processing

#### Upload File
```http
POST /api/upload/file
Content-Type: multipart/form-data

file: [PDF or EPUB file]
```

**Response:**
```json
{
  "file_id": "uuid-string",
  "filename": "document.pdf",
  "file_size": 1048576,
  "content_type": "application/pdf",
  "upload_path": "/storage/uploads/uuid-string.pdf"
}
```

#### Start Conversion
```http
POST /api/convert/start
Content-Type: application/json

{
  "file_id": "uuid-string",
  "voice_model": "fr_FR-siwis-low",
  "length_scale": 1.0,
  "noise_scale": 0.667,
  "noise_w": 0.8,
  "sentence_silence": 0.35
}
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "pending",
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### Get Conversion Status
```http
GET /api/convert/status/{job_id}
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "processing",
  "progress_percent": 45,
  "created_at": "2024-01-01T12:00:00Z",
  "completed_at": null,
  "audio_file_url": null,
  "error_message": null
}
```

### Audio Serving

#### Stream Audio File
```http
GET /api/audio/{job_id}
```
Returns audio file with proper content-type headers for streaming.

#### Download Audio File
```http
GET /api/audio/{job_id}/download
```
Forces download with appropriate filename.

#### Preview Audio
```http
GET /api/preview/audio/{preview_id}
```
Serves generated preview audio files.

### Utility Endpoints

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "app": "TTS Audio Book Converter",
  "version": "1.0.0"
}
```

#### Cleanup Old Previews
```http
POST /api/preview/cleanup?max_age_hours=24
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# Application
DEBUG=true
APP_NAME="TTS Audio Book Converter"
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
DEFAULT_PAUSE_BETWEEN_BLOCKS=1.0

# Storage Paths (relative to backend directory)
STORAGE_BASE_PATH=storage
UPLOAD_DIR=storage/uploads
OUTPUT_DIR=storage/outputs
TEMP_DIR=storage/temp
VOICES_BASE_PATH=voices
```

### Voice Model Structure

Voice models should be organized as follows:

```
voices/
├── fr/                    # Language family
│   └── fr_FR/             # Locale
│       ├── siwis/         # Dataset
│       │   ├── low/       # Quality level
│       │   │   ├── fr_FR-siwis-low.onnx
│       │   │   └── fr_FR-siwis-low.onnx.json
│       │   └── medium/
│       │       ├── fr_FR-siwis-medium.onnx
│       │       └── fr_FR-siwis-medium.onnx.json
│       ├── tom/
│       │   └── medium/
│       │       ├── fr_FR-tom-medium.onnx
│       │       └── fr_FR-tom-medium.onnx.json
│       └── ...
└── en/                    # Other languages
    └── ...
```

### Voice Metadata Format

Each voice model includes a JSON metadata file:

```json
{
  "audio": {
    "quality": "medium",
    "sample_rate": 22050
  },
  "dataset": "siwis",
  "language": {
    "code": "fr_FR",
    "family": "fr",
    "region": "FR",
    "name_native": "Français",
    "name_english": "French",
    "country_english": "France"
  },
  "model_card": "https://huggingface.co/rhasspy/piper-voices",
  "num_speakers": 1,
  "speaker_id_map": {},
  "version": "1.0.0"
}
```

## 🛠️ Development

### Setting Up Development Environment

1. **Install Python dependencies**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Install Piper TTS**:
   ```bash
   pip install piper-tts
   ```

3. **Download voice models** (optional - basic voices included):
   ```bash
   # French voices
   wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx
   wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/low/fr_FR-siwis-low.onnx.json
   ```

4. **Create storage directories**:
   ```bash
   mkdir -p storage/{uploads,outputs,temp}
   ```

5. **Start development server**:
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   ```

### Code Style and Quality

**Formatting and Linting:**
```bash
# Install development tools
pip install black isort flake8 mypy pytest

# Format code
black app/
isort app/

# Type checking
mypy app/

# Linting
flake8 app/
```

**Testing:**
```bash
# Run all tests
pytest

# With coverage
pytest --cov=app tests/

# Specific test file
pytest tests/test_voice_api.py -v
```

### Adding New Features

1. **New API Endpoints:**
   - Create route in `app/api/routes/`
   - Add Pydantic models in `app/models/`
   - Include router in `app/main.py`

2. **New Services:**
   - Implement in `app/services/`
   - Add corresponding tests in `tests/`
   - Update dependencies if needed

3. **Configuration Changes:**
   - Update `app/core/config.py`
   - Document new environment variables
   - Update startup checks if needed

## 🧪 Testing

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── unit/                    # Unit tests
│   ├── test_config.py       # Configuration tests
│   ├── test_voice_models.py # Voice model tests
│   └── test_text_processor.py
└── integration/             # Integration tests
    ├── test_api_routes.py   # API endpoint tests
    ├── test_file_upload.py  # File processing tests
    └── test_tts_pipeline.py # End-to-end TTS tests
```

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test
pytest tests/unit/test_config.py::test_default_configuration -v

# With coverage report
pytest --cov=app --cov-report=html tests/
```

### Test Coverage

Target coverage levels:
- **Critical paths**: >90% (API routes, TTS pipeline)
- **Business logic**: >80% (services, processors)
- **Overall project**: >70%

### Writing New Tests

```python
# Example test for API endpoint
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app" in data
    assert "version" in data

# Example test with fixtures
def test_voice_list(client):
    response = client.get("/api/voice/list")
    assert response.status_code == 200
    data = response.json()
    assert "voices" in data
    assert "count" in data
    assert data["count"] >= 0
```

## 🔍 Troubleshooting

### Common Issues

**"No voices found"**
- Check that voice files exist in `voices/` directory
- Verify file permissions (readable by application)
- Check voice file format (.onnx and .onnx.json pairs)
- Restart application after adding new voices

**"Piper command not found"**
- Install Piper TTS: `pip install piper-tts`
- Verify installation: `which piper`
- Add to PATH if installed in custom location

**"Port already in use"**
- Check running processes: `lsof -i :8001`
- Use different port: `--port 8002`
- Kill existing process if needed

**"Permission denied" errors**
- Check file permissions in storage directories
- Ensure application has write access to storage paths
- Create directories if they don't exist

### Debug Mode

Enable detailed logging:

```bash
DEBUG=true LOG_LEVEL=debug python -m uvicorn app.main:app --reload --log-level debug
```

### Health Diagnostics

```bash
# Check application health
curl http://localhost:8001/health

# Verify voice detection
curl http://localhost:8001/api/voice/list | jq '.count'

# Test TTS functionality
curl -X POST http://localhost:8001/api/preview/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Test", "voice_model": "fr_FR-siwis-low"}'
```

## 📈 Performance Considerations

### Optimization Tips

1. **Async Processing**: Use async/await for I/O operations
2. **Chunked Processing**: Break large texts into manageable chunks
3. **File Management**: Implement cleanup routines for temporary files
4. **Caching**: Cache voice metadata and default parameters
5. **Resource Limits**: Set appropriate limits for file sizes and concurrent jobs

### Monitoring

Key metrics to monitor:
- Response times for API endpoints
- Voice model loading times
- Audio generation speed (characters per second)
- Storage usage and cleanup effectiveness
- Memory usage during conversion

## 📄 License

This backend is part of the Audio Book Converter project, licensed under MIT License.

## 🙏 Acknowledgments

- **[Piper TTS](https://github.com/rhasspy/piper)** - Neural text-to-speech engine
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - Data validation library
- **[Uvicorn](https://www.uvicorn.org/)** - ASGI server implementation

---

**Backend ready! Start with: `python -m uvicorn app.main:app --reload --port 8001`**