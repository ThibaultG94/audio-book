"""Tests for enhanced voice management system."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from app.services.voice_manager import (
    VoiceManager, VoiceGender, VoiceQuality, UsageType,
    VoiceMetadata, VoiceSpeaker, VoiceTechnical
)


class TestVoiceManager:
    """Test suite for VoiceManager class."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.voices_dir = self.temp_dir / "voices"
        self.voices_dir.mkdir(parents=True)
        
        # Mock settings
        with patch('app.services.voice_manager.settings') as mock_settings:
            mock_settings.voices_dir = self.voices_dir
            self.voice_manager = VoiceManager()
    
    def create_mock_voice_files(self):
        """Create mock voice files for testing."""
        # Create directory structure
        siwis_low = self.voices_dir / "fr" / "fr_FR" / "siwis" / "low"
        tom_medium = self.voices_dir / "fr" / "fr_FR" / "tom" / "medium"
        
        for path in [siwis_low, tom_medium]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Create mock ONNX files
        siwis_onnx = siwis_low / "fr_FR-siwis-low.onnx"
        tom_onnx = tom_medium / "fr_FR-tom-medium.onnx"
        
        siwis_onnx.write_bytes(b"mock_onnx_content")
        tom_onnx.write_bytes(b"mock_onnx_content")
        
        # Create JSON metadata
        siwis_json = siwis_low / "fr_FR-siwis-low.onnx.json"
        tom_json = tom_medium / "fr_FR-tom-medium.onnx.json"
        
        siwis_metadata = {
            "audio": {"sample_rate": 16000, "quality": "low"},
            "language": {
                "code": "fr_FR",
                "name_english": "French",
                "name_native": "Français"
            },
            "dataset": "siwis"
        }
        
        tom_metadata = {
            "audio": {"sample_rate": 22050, "quality": "medium"}, 
            "language": {
                "code": "fr_FR",
                "name_english": "French",
                "name_native": "Français"
            },
            "dataset": "tom"
        }
        
        siwis_json.write_text(json.dumps(siwis_metadata))
        tom_json.write_text(json.dumps(tom_metadata))
        
        return [siwis_onnx, tom_onnx]

    def test_voice_manager_initialization(self):
        """Test VoiceManager initialization."""
        assert isinstance(self.voice_manager, VoiceManager)
        assert self.voice_manager.voices_metadata is not None
    
    def test_load_metadata_from_files(self):
        """Test loading metadata from existing files."""
        self.create_mock_voice_files()
        
        # Generate metadata
        self.voice_manager.generate_metadata_from_models()
        
        # Check loaded voices
        voices = self.voice_manager.get_all_voices()
        assert len(voices) == 2
        
        # Check voice characteristics
        siwis_voice = next((v for v in voices if "siwis" in v.name.lower()), None)
        tom_voice = next((v for v in voices if "tom" in v.name.lower()), None)
        
        assert siwis_voice is not None
        assert tom_voice is not None
        
        assert siwis_voice.speaker.gender == VoiceGender.FEMALE
        assert tom_voice.speaker.gender == VoiceGender.MALE
        
        assert siwis_voice.technical.quality == VoiceQuality.LOW
        assert tom_voice.technical.quality == VoiceQuality.MEDIUM

    def test_voice_filtering(self):
        """Test voice filtering functionality."""
        self.create_mock_voice_files()
        self.voice_manager.generate_metadata_from_models()
        
        # Filter by gender
        female_voices = self.voice_manager.filter_voices(gender=VoiceGender.FEMALE)
        male_voices = self.voice_manager.filter_voices(gender=VoiceGender.MALE)
        
        assert len(female_voices) == 1
        assert len(male_voices) == 1
        
        # Filter by quality
        low_quality = self.voice_manager.filter_voices(quality=VoiceQuality.LOW)
        medium_quality = self.voice_manager.filter_voices(quality=VoiceQuality.MEDIUM)
        
        assert len(low_quality) == 1
        assert len(medium_quality) == 1

    def test_voice_recommendations(self):
        """Test voice recommendation system."""
        self.create_mock_voice_files()
        self.voice_manager.generate_metadata_from_models()
        
        # Test usage-based recommendations
        audiobook_voices = self.voice_manager.get_recommendations_for_usage(UsageType.AUDIOBOOK)
        assert len(audiobook_voices) >= 1
        
        # Test quality-based recommendations
        best_voices = self.voice_manager.get_best_quality_voices()
        assert len(best_voices) == 2
        
        # Check ordering (high quality first)
        qualities = [v.technical.quality.value for v in best_voices]
        assert qualities[0] in ["medium", "high"]  # Higher quality should be first

    def test_voice_statistics(self):
        """Test voice statistics generation."""
        self.create_mock_voice_files()
        self.voice_manager.generate_metadata_from_models()
        
        stats = self.voice_manager.get_voice_statistics()
        
        assert stats["total"] == 2
        assert stats["by_gender"]["female"] == 1
        assert stats["by_gender"]["male"] == 1
        assert stats["by_quality"]["low"] == 1
        assert stats["by_quality"]["medium"] == 1
        assert stats["total_size_mb"] > 0

    def test_metadata_persistence(self):
        """Test saving and loading metadata."""
        self.create_mock_voice_files()
        self.voice_manager.generate_metadata_from_models()
        
        # Save metadata
        self.voice_manager.save_metadata()
        
        # Create new manager instance
        with patch('app.services.voice_manager.settings') as mock_settings:
            mock_settings.voices_dir = self.voices_dir
            new_manager = VoiceManager()
        
        # Check loaded data
        original_voices = self.voice_manager.get_all_voices()
        loaded_voices = new_manager.get_all_voices()
        
        assert len(original_voices) == len(loaded_voices)

    def test_voice_characteristics_inference(self):
        """Test automatic inference of voice characteristics."""
        # Test gender inference
        gender, avatar, color = self.voice_manager._infer_voice_characteristics("tom", "fr_FR-tom-medium")
        assert gender == VoiceGender.MALE
        assert avatar == "👨‍💼"
        
        gender, avatar, color = self.voice_manager._infer_voice_characteristics("siwis", "fr_FR-siwis-low") 
        assert gender == VoiceGender.FEMALE
        assert avatar == "👩‍💼"
        
        gender, avatar, color = self.voice_manager._infer_voice_characteristics("upmc", "fr_FR-upmc-medium")
        assert gender == VoiceGender.MULTI
        assert avatar == "👫"

    def test_error_handling(self):
        """Test error handling in voice management."""
        # Test with non-existent directory
        with patch('app.services.voice_manager.settings') as mock_settings:
            mock_settings.voices_dir = Path("/non/existent/path")
            manager = VoiceManager()
            
            voices = manager.get_all_voices()
            assert len(voices) == 0

    def test_voice_validation(self):
        """Test voice file validation."""
        voice_files = self.create_mock_voice_files()
        
        # Test with valid files
        self.voice_manager.generate_metadata_from_models()
        voices = self.voice_manager.get_all_voices()
        assert len(voices) == 2
        
        # Test with corrupted file (empty)
        voice_files[0].write_bytes(b"")
        self.voice_manager.generate_metadata_from_models()
        
        # Should still work, file size will be 0
        voices = self.voice_manager.get_all_voices()
        corrupted_voice = next((v for v in voices if v.technical.file_size_mb == 0), None)
        assert corrupted_voice is not None


class TestVoiceMetadataStructure:
    """Test voice metadata data structures."""
    
    def test_voice_metadata_creation(self):
        """Test VoiceMetadata creation and validation."""
        speaker = VoiceSpeaker(
            gender=VoiceGender.FEMALE,
            age_range="adult",
            voice_style="neutral"
        )
        
        technical = VoiceTechnical(
            quality=VoiceQuality.MEDIUM,
            sample_rate=22050,
            dataset="test",
            file_size_mb=50,
            processing_speed="medium"
        )
        
        metadata = VoiceMetadata(
            name="Test Voice",
            display_name="Test Voice (Medium)",
            language={"code": "fr_FR", "name_english": "French"},
            speaker=speaker,
            technical=technical,
            recommended_usage=[UsageType.AUDIOBOOK],
            description="Test voice for unit tests",
            best_for="Testing",
            avatar="🤖",
            color="#FF0000",
            model_path="test/path.onnx"
        )
        
        assert metadata.name == "Test Voice"
        assert metadata.speaker.gender == VoiceGender.FEMALE
        assert metadata.technical.quality == VoiceQuality.MEDIUM
        assert UsageType.AUDIOBOOK in metadata.recommended_usage

    def test_enum_values(self):
        """Test enum values are correct."""
        # Test VoiceGender
        assert VoiceGender.FEMALE.value == "female"
        assert VoiceGender.MALE.value == "male"
        assert VoiceGender.MULTI.value == "multi"
        
        # Test VoiceQuality
        assert VoiceQuality.LOW.value == "low"
        assert VoiceQuality.MEDIUM.value == "medium"
        assert VoiceQuality.HIGH.value == "high"
        
        # Test UsageType
        assert UsageType.AUDIOBOOK.value == "audiobook"
        assert UsageType.NEWS.value == "news"
        assert UsageType.STORYTELLING.value == "storytelling"


class TestVoiceAPIIntegration:
    """Integration tests for voice API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)
    
    def test_voices_endpoint(self, client):
        """Test /api/preview/voices endpoint."""
        response = client.get("/api/preview/voices")
        assert response.status_code == 200
        
        data = response.json()
        assert "voices" in data
        assert "count" in data
        assert isinstance(data["voices"], list)
    
    def test_voice_parameters_endpoint(self, client):
        """Test /api/preview/parameters/defaults endpoint."""
        response = client.get("/api/preview/parameters/defaults")
        assert response.status_code == 200
        
        data = response.json()
        assert "parameters" in data
        assert "presets" in data
        
        # Check required parameters exist
        params = data["parameters"]
        required_params = ["length_scale", "noise_scale", "noise_w", "sentence_silence"]
        for param in required_params:
            assert param in params
            assert "default" in params[param]
            assert "range" in params[param]
    
    def test_voice_installation_guide(self, client):
        """Test /api/preview/voices/install-guide endpoint."""
        response = client.get("/api/preview/voices/install-guide")
        assert response.status_code == 200
        
        data = response.json()
        assert "installation_guide" in data
        assert "recommended_voices" in data
        assert "current_status" in data


# Pytest fixtures and configuration
@pytest.fixture(scope="session")
def temp_voices_dir():
    """Create temporary voices directory for testing."""
    import tempfile
    import shutil
    
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_piper_binary():
    """Mock Piper TTS binary for testing."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "test audio generated"
        mock_run.return_value.stderr = ""
        yield mock_run


# Integration test for complete workflow
def test_voice_workflow_integration(temp_voices_dir, mock_piper_binary):
    """Test complete voice workflow from installation to usage."""
    
    # 1. Setup voice files
    voices_dir = temp_voices_dir / "voices"
    voices_dir.mkdir()
    
    # Create mock voice structure
    tom_voice = voices_dir / "fr" / "fr_FR" / "tom" / "medium"
    tom_voice.mkdir(parents=True)
    
    onnx_file = tom_voice / "fr_FR-tom-medium.onnx"
    onnx_file.write_bytes(b"mock_onnx_data" * 1000)  # ~13KB
    
    json_file = tom_voice / "fr_FR-tom-medium.onnx.json"
    json_file.write_text(json.dumps({
        "audio": {"sample_rate": 22050, "quality": "medium"},
        "language": {"code": "fr_FR", "name_english": "French"},
        "dataset": "tom"
    }))
    
    # 2. Initialize voice manager
    with patch('app.services.voice_manager.settings') as mock_settings:
        mock_settings.voices_dir = voices_dir
        manager = VoiceManager()
    
    # 3. Generate and validate metadata
    manager.generate_metadata_from_models()
    voices = manager.get_all_voices()
    
    assert len(voices) == 1
    tom_voice_meta = voices[0]
    
    assert tom_voice_meta.name == "Tom"
    assert tom_voice_meta.speaker.gender == VoiceGender.MALE
    assert tom_voice_meta.technical.quality == VoiceQuality.MEDIUM
    
    # 4. Test filtering and recommendations
    male_voices = manager.filter_voices(gender=VoiceGender.MALE)
    assert len(male_voices) == 1
    
    audiobook_voices = manager.get_recommendations_for_usage(UsageType.AUDIOBOOK)
    assert len(audiobook_voices) == 1
    
    # 5. Test statistics
    stats = manager.get_voice_statistics()
    assert stats["total"] == 1
    assert stats["by_gender"]["male"] == 1
    assert stats["total_size_mb"] > 0
    
    print("✅ Complete voice workflow test passed")


if __name__ == "__main__":
    # Run specific tests
    pytest.main([__file__, "-v", "--tb=short"])