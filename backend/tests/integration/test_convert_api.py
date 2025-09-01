"""Integration tests for conversion API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from app.services.conversion_service import conversion_service


class TestConversionAPI:
    """Test conversion API endpoints."""
    
    def test_start_conversion_success(self, client, mock_pdf_file, mock_voice_file):
        """Test successful conversion start."""
        # Upload file first
        with open(mock_pdf_file, "rb") as f:
            upload_response = client.post(
                "/api/upload/file",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        
        file_id = upload_response.json()["file_id"]
        
        # Mock conversion service
        with patch.object(conversion_service, 'start_conversion') as mock_start:
            mock_start.return_value = "test-job-123"
            
            response = client.post(
                "/api/convert/start",
                json={
                    "file_id": file_id,
                    "voice_model": str(mock_voice_file),
                    "length_scale": 1.0,
                    "noise_scale": 0.667,
                    "noise_w": 0.8,
                    "sentence_silence": 0.35,
                    "output_format": "wav"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "test-job-123"
        assert data["status"] == "started"
    
    def test_get_conversion_status(self, client):
        """Test getting conversion status."""
        job_id = "test-job-456"
        
        # Mock conversion service
        with patch.object(conversion_service, 'get_conversion_status') as mock_status:
            mock_status.return_value = {
                "job_id": job_id,
                "status": "processing",
                "progress": 50,
                "started_at": "2024-01-01T00:00:00",
                "completed_at": None,
                "error": None,
                "steps": {
                    "extraction": {"status": "completed", "progress": 100},
                    "processing": {"status": "in_progress", "progress": 50}
                },
                "output_file": None,
                "duration_estimate": None,
                "chapters": []
            }
            
            response = client.get(f"/api/convert/status/{job_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert data["status"] == "processing"
        assert data["progress"] == 50
    
    def test_cancel_conversion(self, client):
        """Test cancelling a conversion."""
        job_id = "test-job-789"
        
        with patch.object(conversion_service, 'cancel_conversion') as mock_cancel:
            mock_cancel.return_value = True
            
            response = client.post(f"/api/convert/cancel/{job_id}")
        
        assert response.status_code == 200
        assert response.json()["message"] == "Conversion cancelled successfully"
    
    def test_list_conversions(self, client):
        """Test listing conversions."""
        with patch.object(conversion_service, 'list_conversions') as mock_list:
            mock_list.return_value = [
                {"job_id": "job1", "status": "completed"},
                {"job_id": "job2", "status": "processing"}
            ]
            
            response = client.get("/api/convert/list")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["conversions"]) == 2