"""Test configuration and fixtures."""

import asyncio
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import create_app
from app.core.config import get_settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_storage() -> Generator[Path, None, None]:
    """Create temporary storage directories for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create subdirectories
        (temp_path / "uploads").mkdir()
        (temp_path / "outputs").mkdir()
        (temp_path / "temp").mkdir()
        (temp_path / "voices").mkdir()
        
        yield temp_path


@pytest.fixture
def test_app(temp_storage):
    """Create test FastAPI app with temporary storage."""
    app = create_app()
    
    # Override settings for testing
    settings = get_settings()
    settings.STORAGE_BASE_PATH = temp_storage
    settings.UPLOAD_DIR = temp_storage / "uploads"
    settings.OUTPUT_DIR = temp_storage / "outputs"
    settings.TEMP_DIR = temp_storage / "temp"
    settings.VOICES_BASE_PATH = temp_storage / "voices"
    
    return app


@pytest.fixture
def client(test_app) -> TestClient:
    """Create test client."""
    return TestClient(test_app)


@pytest.fixture
async def async_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    async with AsyncClient(app=test_app, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def sample_voice_files(temp_storage) -> Path:
    """Create sample voice model files for testing."""
    voice_dir = temp_storage / "voices" / "fr" / "fr_FR" / "test" / "low"
    voice_dir.mkdir(parents=True)
    
    # Create dummy voice files
    model_file = voice_dir / "fr_FR-test-low.onnx"
    config_file = voice_dir / "fr_FR-test-low.onnx.json"
    
    model_file.write_bytes(b"dummy model data")
    
    config_data = {
        "name": "Test Voice",
        "language": {"code": "fr_FR"},
        "dataset": "test-dataset",
        "audio": {"sample_rate": 22050},
        "num_speakers": 1,
        "recommended_usage": ["test", "audiobook"]
    }
    
    import json
    config_file.write_text(json.dumps(config_data))
    
    return voice_dir


@pytest.fixture
def sample_text_files(temp_storage) -> dict:
    """Create sample text files for testing."""
    files = {}
    
    # Sample PDF content (mock)
    pdf_path = temp_storage / "uploads" / "sample.pdf"
    pdf_path.write_bytes(b"dummy pdf content")
    files["pdf"] = pdf_path
    
    # Sample text content
    txt_path = temp_storage / "uploads" / "sample.txt"
    txt_path.write_text("Ceci est un texte de test pour la synthèse vocale.")
    files["txt"] = txt_path
    
    return files