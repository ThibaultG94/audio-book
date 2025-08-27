"""Tests for voice service."""

import json
from pathlib import Path

import pytest

from app.services.voice_service import VoiceService
from app.models.voice import VoiceQuality


class TestVoiceService:
    """Tests for VoiceService class."""
    
    def test_get_available_voices_empty(self, temp_storage):
        """Test getting voices from empty directory."""
        service = VoiceService()
        service.voices_dir = temp_storage / "voices"
        
        response = service.get_available_voices()
        
        assert response.count == 0
        assert response.voices == []
    
    def test_get_available_voices_with_sample(self, temp_storage, sample_voice_files):
        """Test getting voices with sample voice files."""
        service = VoiceService()
        service.voices_dir = temp_storage / "voices"
        
        response = service.get_available_voices()
        
        assert response.count == 1
        voice = response.voices[0]
        
        assert voice.name == "Test Voice"
        assert voice.language == "fr_FR"
        assert voice.quality == VoiceQuality.LOW
        assert voice.is_available == True
        assert "test" in voice.metadata.recommended_usage
    
    def test_get_voice_by_id_success(self, temp_storage, sample_voice_files):
        """Test getting specific voice by ID."""
        service = VoiceService()
        service.voices_dir = temp_storage / "voices"
        
        # Get available voices first
        response = service.get_available_voices()
        voice_id = response.voices[0].id
        
        # Get voice by ID
        voice = service.get_voice_by_id(voice_id)
        
        assert voice is not None
        assert voice.id == voice_id
        assert voice.name == "Test Voice"
    
    def test_get_voice_by_id_not_found(self, temp_storage):
        """Test getting non-existent voice by ID."""
        service = VoiceService()
        service.voices_dir = temp_storage / "voices"
        
        voice = service.get_voice_by_id("nonexistent-voice")
        
        assert voice is None
    
    def test_is_voice_available_true(self, temp_storage, sample_voice_files):
        """Test voice availability check for existing voice."""
        service = VoiceService()
        service.voices_dir = temp_storage / "voices"
        
        response = service.get_available_voices()
        voice_id = response.voices[0].id
        
        is_available = service.is_voice_available(voice_id)
        
        assert is_available == True
    
    def test_is_voice_available_false(self, temp_storage):
        """Test voice availability check for non-existent voice."""
        service = VoiceService()
        service.voices_dir = temp_storage / "voices"
        
        is_available = service.is_voice_available("nonexistent-voice")
        
        assert is_available == False
    
    def test_quality_determination(self, temp_storage):
        """Test quality determination from file path."""
        service = VoiceService()
        
        # Test quality detection from path
        low_path = Path("/voices/test/low/model.onnx")
        medium_path = Path("/voices/test/medium/model.onnx")
        high_path = Path("/voices/test/high/model.onnx")
        
        assert service._determine_quality(low_path, {}) == VoiceQuality.LOW
        assert service._determine_quality(medium_path, {}) == VoiceQuality.MEDIUM
        assert service._determine_quality(high_path, {}) == VoiceQuality.HIGH
