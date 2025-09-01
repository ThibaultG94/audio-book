"""Pytest configuration and shared fixtures."""

import pytest
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app
from app.core.config import settings


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_voice_file(temp_dir):
    """Create mock voice model file."""
    voice_file = temp_dir / "test_voice.onnx"
    voice_file.write_text("mock voice model")
    return voice_file


@pytest.fixture
def mock_pdf_file(temp_dir):
    """Create mock PDF file."""
    pdf_file = temp_dir / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 test content")
    return pdf_file


@pytest.fixture
def mock_piper_command():
    """Mock piper TTS command."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(
            returncode=0,
            stdout=b"mock audio data",
            stderr=b""
        )
        yield mock_run


@pytest.fixture(autouse=True)
def setup_test_environment(temp_dir, monkeypatch):
    """Setup test environment with temporary directories."""
    # Override settings for tests
    monkeypatch.setattr(settings, "UPLOAD_DIR", temp_dir / "uploads")
    monkeypatch.setattr(settings, "OUTPUT_DIR", temp_dir / "outputs")
    monkeypatch.setattr(settings, "TEMP_DIR", temp_dir / "temp")
    monkeypatch.setattr(settings, "VOICES_BASE_PATH", temp_dir / "voices")
    
    # Create directories
    (temp_dir / "uploads").mkdir(exist_ok=True)
    (temp_dir / "outputs").mkdir(exist_ok=True)
    (temp_dir / "temp").mkdir(exist_ok=True)
    (temp_dir / "voices").mkdir(exist_ok=True)