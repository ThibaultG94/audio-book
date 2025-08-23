"""Tests for audio routes."""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import wave

from app.main import app
from app.core.config import settings

client = TestClient(app)

@pytest.fixture
def temp_audio_file():
    """Create a temporary WAV file for testing."""
    # Create a minimal valid WAV file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
        # Create a minimal WAV file (1 second of silence at 16kHz)
        with wave.open(tmp_file.name, 'wb') as wav_file:
            wav_file.setnchannels(1)  # mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(16000)  # 16kHz
            # Write 1 second of silence
            silence = b'\x00\x00' * 16000
            wav_file.writeframes(silence)
    
    return Path(tmp_file.name)

def test_get_audio_file_not_found():
    """Test getting non-existent audio file."""
    response = client.get("/api/audio/nonexistent-job-id")
    assert response.status_code == 404
    assert "Audio file not found" in response.json()["detail"]

def test_get_audio_file_invalid_job_id():
    """Test getting audio with invalid job ID."""
    response = client.get("/api/audio/short")
    assert response.status_code == 400
    assert "Invalid job ID" in response.json()["detail"]

def test_check_audio_file_not_found():
    """Test HEAD request for non-existent file."""
    response = client.head("/api/audio/nonexistent-job-id")
    assert response.status_code == 404

def test_get_audio_info_not_found():
    """Test getting info for non-existent audio file."""
    response = client.get("/api/audio/info/nonexistent-job-id")
    assert response.status_code == 404

def test_get_audio_info_invalid_job_id():
    """Test getting info with invalid job ID."""
    response = client.get("/api/audio/info/bad")
    assert response.status_code == 400

# Note: For full integration tests with actual files,
# we would need to set up proper test fixtures with temp directories
# and mock the settings.outputs_dir