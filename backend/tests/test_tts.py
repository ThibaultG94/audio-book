"""
Tests for TTS Service
"""
import pytest
import tempfile
import json
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import shutil

from app.services.tts import TTSService, ConversionJob, ConversionStatus


class TestTTSService:
    """Test TTS conversion functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        with patch('app.services.tts.TTSService._verify_piper'):
            self.tts = TTSService()
    
    def teardown_method(self):
        """Cleanup test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('app.services.tts.TTSService._verify_piper')
    def test_initialization(self, mock_verify):
        """Test TTS service initialization"""
        service = TTSService(
            model_path="/custom/model.onnx",
            output_format="wav",
            max_workers=4
        )
        
        assert service.model_path == "/custom/model.onnx"
        assert service.output_format == "wav"
        assert service.max_workers == 4
        mock_verify.assert_called_once()
    
    @patch('subprocess.run')
    def test_verify_piper_success(self, mock_run):
        """Test Piper verification success"""
        mock_run.return_value = MagicMock(returncode=0, stdout="piper version 1.0")
        
        service = TTSService()
        # Should not raise an exception
    
    @patch('subprocess.run')
    def test_verify_piper_failure(self, mock_run):
        """Test Piper verification failure"""
        mock_run.side_effect = FileNotFoundError()
        
        with pytest.raises(RuntimeError, match="Piper TTS not found"):
            service = TTSService()
    
    @pytest.mark.asyncio
    @patch('subprocess.run')
    async def test_convert_book_success(self, mock_subprocess):
        """Test successful book conversion"""
        # Mock subprocess for Piper
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        # Create test manifest
        manifest = {
            "book_id": "test_123",
            "book_title": "Test Book",
            "total_chapters": 2,
            "chapters": [
                {
                    "index": 0,
                    "title": "Chapter 1",
                    "filename": "001_TestBook_Chapter1",
                    "text_file": f"{self.temp_dir}/ch1.txt",
                    "status": "pending",
                    "estimated_duration_seconds": 120
                },
                {
                    "index": 1,
                    "title": "Chapter 2",
                    "filename": "002_TestBook_Chapter2",
                    "text_file": f"{self.temp_dir}/ch2.txt",
                    "status": "pending",
                    "estimated_duration_seconds": 120
                }
            ]
        }
        
        # Create chapter text files
        Path(f"{self.temp_dir}/ch1.txt").write_text("Chapter 1 content")
        Path(f"{self.temp_dir}/ch2.txt").write_text("Chapter 2 content")
        
        # Save manifest
        manifest_path = Path(self.temp_dir) / "manifest.json"
        manifest_path.write_text(json.dumps(manifest))
        
        # Mock audio file creation
        with patch.object(Path, 'exists', return_value=True):
            with patch('app.services.tts.TTSService._create_archive', return_value="test.zip"):
                # Run conversion
                job = await self.tts.convert_book(
                    book_id="test_123",
                    manifest_path=str(manifest_path)
                )
        
        # Verify job
        assert job.book_id == "test_123"
        assert job.book_title == "Test Book"
        assert job.total_chapters == 2
        assert job.status == ConversionStatus.COMPLETED
        assert job.chapters_completed > 0
        assert job.error is None
    
    @pytest.mark.asyncio
    async def test_convert_book_with_progress_callback(self):
        """Test conversion with progress callback"""
        progress_updates = []
        
        async def progress_callback(job_id, data):
            progress_updates.append(data)
        
        # Create minimal manifest
        manifest = {
            "book_id": "test_456",
            "book_title": "Progress Test",
            "total_chapters": 1,
            "chapters": [
                {
                    "index": 0,
                    "title": "Chapter 1",
                    "text_file": f"{self.temp_dir}/ch1.txt",
                    "status": "pending",
                    "estimated_duration_seconds": 60
                }
            ]
        }
        
        Path(f"{self.temp_dir}/ch1.txt").write_text("Test content")
        manifest_path = Path(self.temp_dir) / "manifest.json"
        manifest_path.write_text(json.dumps(manifest))
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch.object(Path, 'exists', return_value=True):
                await self.tts.convert_book(
                    book_id="test_456",
                    manifest_path=str(manifest_path),
                    progress_callback=progress_callback
                )
        
        # Check progress updates were sent
        assert len(progress_updates) > 0
        assert any('progress' in update for update in progress_updates)
    
    @patch('subprocess.run')
    def test_convert_chapter(self, mock_subprocess):
        """Test single chapter conversion"""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        # Create test chapter
        chapter = {
            'title': 'Test Chapter',
            'text_file': f'{self.temp_dir}/chapter.txt'
        }
        
        Path(chapter['text_file']).write_text("Chapter content")
        
        # Mock WAV file creation
        with patch.object(Path, 'exists', return_value=True):
            result = self.tts._convert_chapter(chapter, Path(self.temp_dir))
        
        assert result.name.endswith('.mp3') or result.name.endswith('.wav')
    
    @patch('subprocess.run')
    def test_convert_to_mp3(self, mock_subprocess):
        """Test WAV to MP3 conversion"""
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        wav_path = Path(self.temp_dir) / "test.wav"
        mp3_path = Path(self.temp_dir) / "test.mp3"
        
        # Create dummy WAV file
        wav_path.write_bytes(b"fake wav content")
        
        self.tts._convert_to_mp3(wav_path, mp3_path)
        
        # Check ffmpeg was called correctly
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert "ffmpeg" in call_args
        assert str(wav_path) in call_args
        assert str(mp3_path) in call_args
    
    def test_job_tracking(self):
        """Test job status tracking"""
        # Create test job
        job = ConversionJob(
            job_id="test_job_1",
            book_id="book_123",
            book_title="Test Book",
            total_chapters=5
        )
        
        self.tts.jobs["test_job_1"] = job
        
        # Get status
        status = self.tts.get_job_status("test_job_1")
        
        assert status is not None
        assert status['job_id'] == "test_job_1"
        assert status['book_title'] == "Test Book"
        assert status['status'] == "pending"
        assert status['chapters_completed'] == 0
        
        # Update job
        job.status = ConversionStatus.PROCESSING
        job.chapters_completed = 2
        job.current_chapter = "Chapter 3"
        
        status = self.tts.get_job_status("test_job_1")
        assert status['status'] == "processing"
        assert status['chapters_completed'] == 2
        assert status['current_chapter'] == "Chapter 3"
        
        # Test non-existent job
        status = self.tts.get_job_status("non_existent")
        assert status is None
    
    def test_cancel_job(self):
        """Test job cancellation"""
        # Create processing job
        job = ConversionJob(
            job_id="test_job_cancel",
            book_id="book_456",
            book_title="Cancel Test",
            total_chapters=3,
            status=ConversionStatus.PROCESSING
        )
        
        self.tts.jobs["test_job_cancel"] = job
        
        # Cancel job
        success = self.tts.cancel_job("test_job_cancel")
        
        assert success
        assert job.status == ConversionStatus.CANCELLED
        
        # Try to cancel completed job
        job.status = ConversionStatus.COMPLETED
        success = self.tts.cancel_job("test_job_cancel")
        assert not success
        
        # Try to cancel non-existent job
        success = self.tts.cancel_job("non_existent")
        assert not success
    
    def test_cleanup_job(self):
        """Test job cleanup"""
        # Add test job
        job = ConversionJob(
            job_id="test_cleanup",
            book_id="book_789",
            book_title="Cleanup Test",
            total_chapters=1
        )
        
        self.tts.jobs["test_cleanup"] = job
        
        # Cleanup
        self.tts.cleanup_job("test_cleanup")
        
        # Job should be removed
        assert "test_cleanup" not in self.tts.jobs
    
    def test_generate_readme(self):
        """Test README generation for archive"""
        job = ConversionJob(
            job_id="test_readme",
            book_id="book_readme",
            book_title="README Test Book",
            total_chapters=2,
            chapters_completed=2
        )
        
        manifest = {
            'book_title': 'README Test Book',
            'author': 'Test Author',
            'chapters': [
                {
                    'index': 0,
                    'title': 'Chapter 1',
                    'status': 'completed',
                    'estimated_duration_seconds': 300
                },
                {
                    'index': 1,
                    'title': 'Chapter 2',
                    'status': 'completed',
                    'estimated_duration_seconds': 450
                }
            ]
        }
        
        readme = self.tts._generate_readme(job, manifest)
        
        assert "README Test Book" in readme
        assert "Test Author" in readme
        assert "Chapter 1" in readme
        assert "Chapter 2" in readme
        assert "5:00" in readme  # 300 seconds
        assert "7:30" in readme  # 450 seconds
        assert "Piper TTS" in readme
    
    @pytest.mark.asyncio
    @patch('zipfile.ZipFile')
    async def test_create_archive(self, mock_zipfile):
        """Test ZIP archive creation"""
        mock_zip = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        
        job = ConversionJob(
            job_id="test_archive",
            book_id="book_archive",
            book_title="Archive Test",
            total_chapters=1,
            chapters_completed=1
        )
        
        manifest = {
            'chapters': [
                {
                    'status': 'completed',
                    'audio_file': f'{self.temp_dir}/chapter1.mp3',
                    'filename': '001_TestBook_Chapter1'
                }
            ]
        }
        
        # Create fake audio file
        audio_file = Path(self.temp_dir) / "chapter1.mp3"
        audio_file.write_bytes(b"fake audio")
        
        result = await self.tts._create_archive(job, manifest)
        
        assert result.endswith(".zip")
        mock_zip.write.assert_called()
        mock_zip.writestr.assert_called()  # For manifest and README