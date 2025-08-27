"""Tests for configuration management."""

import pytest
from pathlib import Path
from unittest.mock import patch

from app.core.config import Settings, get_settings


def test_settings_creation():
    """Test basic settings creation."""
    settings = Settings()
    
    assert settings.APP_NAME == "TTS Audio Book Converter"
    assert settings.DEBUG is False
    assert settings.HOST == "0.0.0.0"
    assert settings.PORT == 8000
    assert isinstance(settings.ALLOWED_ORIGINS, list)
    assert "http://localhost:3000" in settings.ALLOWED_ORIGINS


def test_settings_paths():
    """Test path configurations."""
    settings = Settings()
    
    assert isinstance(settings.BASE_DIR, Path)
    assert isinstance(settings.VOICES_BASE_PATH, Path)
    assert isinstance(settings.STORAGE_BASE_PATH, Path)
    assert isinstance(settings.UPLOAD_DIR, Path)
    assert isinstance(settings.OUTPUT_DIR, Path)
    assert isinstance(settings.TEMP_DIR, Path)


def test_tts_configuration():
    """Test TTS-related settings."""
    settings = Settings()
    
    assert settings.DEFAULT_VOICE_MODEL == "fr_FR-siwis-low"
    assert settings.PIPER_EXECUTABLE == "piper"
    assert 0.5 <= settings.DEFAULT_LENGTH_SCALE <= 2.0
    assert 0.0 <= settings.DEFAULT_NOISE_SCALE <= 1.0
    assert 0.0 <= settings.DEFAULT_NOISE_W <= 1.0


def test_file_processing_settings():
    """Test file processing configurations."""
    settings = Settings()
    
    assert settings.MAX_FILE_SIZE > 0
    assert settings.MAX_CHUNK_CHARS > 0
    assert ".pdf" in settings.ALLOWED_EXTENSIONS
    assert ".epub" in settings.ALLOWED_EXTENSIONS


def test_get_settings_cached():
    """Test that get_settings returns cached instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    
    assert settings1 is settings2  # Same instance


@patch.dict("os.environ", {"DEBUG": "true", "PORT": "9000"})
def test_settings_from_environment():
    """Test loading settings from environment variables."""
    # Clear cache to force reload
    get_settings.cache_clear()
    
    settings = get_settings()
    
    assert settings.DEBUG is True
    assert settings.PORT == 9000


def test_settings_validation():
    """Test settings validation."""
    with pytest.raises(ValueError):
        # Invalid port range should raise validation error
        Settings(PORT=-1)
    
    with pytest.raises(ValueError):
        # Invalid file size should raise validation error  
        Settings(MAX_FILE_SIZE=-100)