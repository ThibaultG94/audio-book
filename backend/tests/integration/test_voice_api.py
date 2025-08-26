"""Integration tests for voice management API endpoints."""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from app.main import app

client = TestClient(app)


class TestVoicesAPI:
    """Test voice management API endpoints."""
    
    @pytest.mark.api
    def test_get_voices_endpoint(self):
        """Test GET /api/preview/voices endpoint."""
        response = client.get("/api/preview/voices")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "voices" in data
        assert "default_voice" in data
        assert "count" in data
        assert isinstance(data["voices"], list)
        assert isinstance(data["count"], int)
        
        # If voices are available, check structure
        if data["count"] > 0:
            voice = data["voices"][0]
            required_fields = [
                "model_path", "name", "full_path", "language",
                "dataset", "quality", "sample_rate", "file_size_mb"
            ]
            for field in required_fields:
                assert field in voice
    
    @pytest.mark.api 
    def test_get_voice_parameters_defaults(self):
        """Test GET /api/preview/parameters/defaults endpoint."""
        response = client.get("/api/preview/parameters/defaults")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "parameters" in data
        assert "presets" in data
        
        # Check required parameters exist
        params = data["parameters"]
        required_params = ["length_scale", "noise_scale", "noise_w", "sentence_silence"]
        
        for param in required_params:
            assert param in params
            param_data = params[param]
            assert "default" in param_data
            assert "range" in param_data
            assert "description" in param_data
            assert len(param_data["range"]) == 2
    
    @pytest.mark.api
    def test_get_installation_guide(self):
        """Test GET /api/preview/voices/install-guide endpoint."""
        response = client.get("/api/preview/voices/install-guide")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "installation_guide" in data
        assert "recommended_voices" in data
        assert "current_status" in data
        
        # Check installation guide structure
        guide = data["installation_guide"]
        assert "step_1" in guide
        assert "step_2" in guide
        assert "step_3" in guide
    
    @pytest.mark.api
    @patch('app.api.routes.preview.PreviewTTSEngine')
    def test_tts_preview_endpoint(self, mock_tts_engine):
        """Test POST /api/preview/tts endpoint."""
        # Mock TTS engine
        mock_engine_instance = Mock()
        mock_tts_engine.return_value = mock_engine_instance
        
        # Mock successful preview generation
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 44100  # 1 second of 44.1kHz audio
                
                response = client.post(
                    "/api/preview/tts",
                    json={
                        "text": "Bonjour, ceci est un test.",
                        "voice_model": "voices/fr/fr_FR/tom/medium/fr_FR-tom-medium.onnx",
                        "length_scale": 1.0,
                        "noise_scale": 0.667
                    }
                )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "preview_id" in data
        assert "text" in data
        assert "audio_url" in data
        assert "duration_estimate" in data
        assert "voice_model" in data
        assert "parameters" in data
        
        # Check parameters are returned correctly
        params = data["parameters"]
        assert params["length_scale"] == 1.0
        assert params["noise_scale"] == 0.667
    
    @pytest.mark.api
    def test_tts_preview_validation(self):
        """Test TTS preview endpoint validation."""
        # Test empty text
        response = client.post(
            "/api/preview/tts",
            json={
                "text": "",
                "voice_model": "voices/fr/fr_FR/tom/medium/fr_FR-tom-medium.onnx"
            }
        )
        assert response.status_code == 422  # Validation error
        
        # Test text too long
        response = client.post(
            "/api/preview/tts", 
            json={
                "text": "A" * 1000,  # Too long
                "voice_model": "voices/fr/fr_FR/tom/medium/fr_FR-tom-medium.onnx"
            }
        )
        assert response.status_code == 422
        
        # Test invalid parameters
        response = client.post(
            "/api/preview/tts",
            json={
                "text": "Test text",
                "voice_model": "voices/fr/fr_FR/tom/medium/fr_FR-tom-medium.onnx",
                "length_scale": 5.0  # Out of range
            }
        )
        assert response.status_code == 422
    
    @pytest.mark.api
    @patch('app.api.routes.preview.subprocess.run')
    def test_voice_validation_endpoint(self, mock_subprocess):
        """Test POST /api/preview/voices/validate endpoint."""
        # Mock successful validation
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        response = client.post("/api/preview/voices/validate")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "validation_results" in data
        assert "summary" in data
        assert "recommendations" in data
        
        summary = data["summary"]
        assert "total_models" in summary
        assert "working_models" in summary
        assert "success_rate" in summary
        assert "piper_available" in summary
    
    @pytest.mark.api
    def test_preview_audio_download(self):
        """Test GET /api/preview/audio/{preview_id} endpoint."""
        # Test with invalid preview ID
        response = client.get("/api/preview/audio/invalid-id")
        assert response.status_code == 400  # Invalid preview ID
        
        # Test with non-existent preview
        response = client.get("/api/preview/audio/550e8400-e29b-41d4-a716-446655440000")
        assert response.status_code == 404  # Preview not found
    
    @pytest.mark.api
    def test_preview_cleanup(self):
        """Test POST /api/preview/cleanup endpoint."""
        response = client.post("/api/preview/cleanup")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "deleted" in data
        assert "size_freed_mb" in data
        assert "message" in data
        assert isinstance(data["deleted"], int)
        assert isinstance(data["size_freed_mb"], (int, float))


class TestVoiceSystemIntegration:
    """Integration tests for complete voice system."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_complete_voice_workflow(self, mock_voice_files, mock_piper_command):
        """Test complete workflow from voice selection to preview generation."""
        # 1. Get available voices
        voices_response = client.get("/api/preview/voices")
        assert voices_response.status_code == 200
        voices_data = voices_response.json()
        
        # 2. Get default parameters
        params_response = client.get("/api/preview/parameters/defaults")
        assert params_response.status_code == 200
        params_data = params_response.json()
        
        # 3. Generate preview (mocked)
        if voices_data["count"] > 0:
            voice_path = voices_data["voices"][0]["model_path"]
            
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.stat') as mock_stat:
                    mock_stat.return_value.st_size = 44100
                    
                    preview_response = client.post(
                        "/api/preview/tts",
                        json={
                            "text": "Test complet du système de voix.",
                            "voice_model": voice_path,
                            "length_scale": params_data["parameters"]["length_scale"]["default"],
                            "noise_scale": params_data["parameters"]["noise_scale"]["default"]
                        }
                    )
            
            assert preview_response.status_code == 200
            preview_data = preview_response.json()
            
            # 4. Validate preview data
            assert preview_data["text"] == "Test complet du système de voix."
            assert preview_data["voice_model"] == voice_path
            assert "preview_id" in preview_data
            assert "audio_url" in preview_data
    
    @pytest.mark.integration
    def test_api_error_handling(self):
        """Test API error handling and responses."""
        # Test malformed JSON
        response = client.post(
            "/api/preview/tts",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
        
        # Test missing required fields
        response = client.post(
            "/api/preview/tts",
            json={"voice_model": "test"}  # Missing text field
        )
        assert response.status_code == 422
    
    @pytest.mark.integration
    def test_voice_system_consistency(self):
        """Test consistency across different voice endpoints."""
        # Get voices from main endpoint
        voices_response = client.get("/api/preview/voices")
        assert voices_response.status_code == 200
        voices_data = voices_response.json()
        
        # Check installation guide mentions same voices
        guide_response = client.get("/api/preview/voices/install-guide")
        assert guide_response.status_code == 200
        guide_data = guide_response.json()
        
        # Both endpoints should provide consistent information
        assert isinstance(guide_data["recommended_voices"], dict)
        assert isinstance(voices_data["voices"], list)


if __name__ == "__main__":
    # Run specific API tests
    pytest.main([__file__, "-v", "--tb=short", "-m", "api"])