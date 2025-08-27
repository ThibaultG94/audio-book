"""Tests for preview API endpoints."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


class TestVoicesEndpoint:
    """Tests for /api/preview/voices endpoint."""
    
    def test_get_voices_success(self, client: TestClient, sample_voice_files):
        """Test successful voice listing."""
        response = client.get("/api/preview/voices")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "voices" in data
        assert "count" in data
        assert isinstance(data["voices"], list)
        assert data["count"] >= 0
    
    def test_get_voices_empty_directory(self, client: TestClient, temp_storage):
        """Test voice listing with empty voices directory."""
        response = client.get("/api/preview/voices")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["count"] == 0
        assert data["voices"] == []
    
    def test_get_voices_with_sample_voice(self, client: TestClient, sample_voice_files):
        """Test voice listing with sample voice files."""
        response = client.get("/api/preview/voices")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["count"] == 1
        voice = data["voices"][0]
        
        assert "id" in voice
        assert "name" in voice
        assert voice["name"] == "Test Voice"
        assert voice["language"] == "fr_FR"
        assert voice["is_available"] == True


class TestTTSPreviewEndpoint:
    """Tests for /api/preview/tts endpoint."""
    
    @patch('app.services.tts_engine.TTSEngine.synthesize_text')
    def test_tts_preview_success(self, mock_synthesize, client: TestClient, sample_voice_files):
        """Test successful TTS preview generation."""
        # Mock TTS synthesis
        mock_synthesize.return_value = 2.5  # Mock duration
        
        request_data = {
            "text": "Bonjour, ceci est un test",
            "voice_model": "fr_FR-test-low",
            "length_scale": 1.0,
            "noise_scale": 0.667,
            "noise_w": 0.8,
            "sentence_silence": 0.35
        }
        
        response = client.post("/api/preview/tts", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "audio_url" in data
        assert "duration_seconds" in data
        assert data["voice_used"] == "fr_FR-test-low"
        assert data["text_length"] == len(request_data["text"])
    
    def test_tts_preview_invalid_voice(self, client: TestClient):
        """Test TTS preview with invalid voice model."""
        request_data = {
            "text": "Test text",
            "voice_model": "nonexistent-voice",
            "length_scale": 1.0,
            "noise_scale": 0.667,
            "noise_w": 0.8,
            "sentence_silence": 0.35
        }
        
        response = client.post("/api/preview/tts", json=request_data)
        
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()
    
    def test_tts_preview_empty_text(self, client: TestClient, sample_voice_files):
        """Test TTS preview with empty text."""
        request_data = {
            "text": "",
            "voice_model": "fr_FR-test-low",
            "length_scale": 1.0,
            "noise_scale": 0.667,
            "noise_w": 0.8,
            "sentence_silence": 0.35
        }
        
        response = client.post("/api/preview/tts", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_tts_preview_text_too_long(self, client: TestClient, sample_voice_files):
        """Test TTS preview with text exceeding limit."""
        long_text = "A" * 501  # Exceeds 500 character limit
        
        request_data = {
            "text": long_text,
            "voice_model": "fr_FR-test-low",
            "length_scale": 1.0,
            "noise_scale": 0.667,
            "noise_w": 0.8,
            "sentence_silence": 0.35
        }
        
        response = client.post("/api/preview/tts", json=request_data)
        
        assert response.status_code == 422  # Validation error
