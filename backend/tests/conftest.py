"""Pytest configuration and shared fixtures for voice management tests."""

import pytest
import tempfile
import json
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.voice_manager import VoiceManager
from app.core.config import settings


@pytest.fixture(scope="session")
def temp_voices_directory():
    """Create a temporary voices directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    voices_dir = temp_dir / "voices"
    voices_dir.mkdir()
    
    yield voices_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_voice_files(temp_voices_directory):
    """Create mock voice files for testing."""
    voices_dir = temp_voices_directory
    
    # Create directory structure
    voice_paths = {
        "siwis_low": voices_dir / "fr" / "fr_FR" / "siwis" / "low",
        "tom_medium": voices_dir / "fr" / "fr_FR" / "tom" / "medium",
        "bernard_high": voices_dir / "fr" / "fr_FR" / "bernard" / "high",
    }
    
    voice_files = {}
    
    for voice_name, voice_path in voice_paths.items():
        voice_path.mkdir(parents=True, exist_ok=True)
        
        # Create mock ONNX file
        dataset = voice_name.split('_')[0]
        quality = voice_name.split('_')[1]
        onnx_file = voice_path / f"fr_FR-{dataset}-{quality}.onnx"
        onnx_file.write_bytes(b"mock_onnx_content" * 100)  # ~1.7KB
        
        # Create JSON metadata
        json_file = voice_path / f"fr_FR-{dataset}-{quality}.onnx.json"
        metadata = {
            "audio": {
                "sample_rate": 22050 if quality != "low" else 16000,
                "quality": quality
            },
            "language": {
                "code": "fr_FR",
                "name_english": "French",
                "name_native": "Français"
            },
            "dataset": dataset
        }
        json_file.write_text(json.dumps(metadata, indent=2))
        
        voice_files[voice_name] = {
            "onnx": onnx_file,
            "json": json_file,
            "path": voice_path
        }
    
    return voice_files


@pytest.fixture
def mock_settings(temp_voices_directory):
    """Mock settings for testing."""
    with patch('app.services.voice_manager.settings') as mock_settings_obj:
        mock_settings_obj.voices_dir = temp_voices_directory
        mock_settings_obj.voice_model = str(temp_voices_directory / "fr" / "fr_FR" / "siwis" / "low" / "fr_FR-siwis-low.onnx")
        yield mock_settings_obj


@pytest.fixture
def voice_manager_with_mocks(mock_settings, mock_voice_files):
    """Create VoiceManager instance with mock data."""
    manager = VoiceManager()
    return manager


@pytest.fixture
def sample_voice_metadata():
    """Sample voice metadata for testing."""
    return {
        "version": "1.1.0",
        "voices": {
            "voices/fr/fr_FR/tom/medium/fr_FR-tom-medium.onnx": {
                "name": "Tom",
                "display_name": "Thomas (Tom Medium)",
                "language": {
                    "code": "fr_FR",
                    "name_english": "French",
                    "name_native": "Français"
                },
                "speaker": {
                    "gender": "male",
                    "age_range": "adult",
                    "voice_style": "warm",
                    "accent": "standard"
                },
                "technical": {
                    "quality": "medium",
                    "sample_rate": 22050,
                    "dataset": "tom",
                    "file_size_mb": 52,
                    "processing_speed": "medium"
                },
                "recommended_usage": ["audiobook", "storytelling", "news"],
                "description": "Voix masculine chaleureuse et professionnelle",
                "best_for": "Romans, biographies, actualités",
                "avatar": "👨‍💼",
                "color": "#059669"
            }
        }
    }


@pytest.fixture
def mock_piper_command():
    """Mock Piper TTS command execution."""
    with patch('subprocess.run') as mock_run:
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Audio generated successfully"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        yield mock_run


# Configure pytest
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API test"
    )