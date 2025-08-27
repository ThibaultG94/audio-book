"""Tests for TTS engine."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.tts_engine import TTSEngine, TTSEngineError


class TestTTSEngine:
    """Tests for TTSEngine class."""
    
    def test_init_piper_found(self):
        """Test TTSEngine initialization when Piper is found."""
        with patch('shutil.which', return_value='/usr/local/bin/piper'):
            engine = TTSEngine()
            assert engine.piper_executable == '/usr/local/bin/piper'
    
    def test_init_piper_not_found(self):
        """Test TTSEngine initialization when Piper is not found."""
        with patch('shutil.which', return_value=None):
            with patch('pathlib.Path.exists', return_value=False):
                with pytest.raises(TTSEngineError, match="Piper executable not found"):
                    TTSEngine()
    
    @pytest.mark.asyncio
    async def test_synthesize_text_success(self, temp_storage):
        """Test successful text synthesis."""
        # Mock Piper executable
        with patch('shutil.which', return_value='/usr/local/bin/piper'):
            engine = TTSEngine()
            
            # Mock subprocess
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate.return_value = (b"output", b"")
            
            with patch('asyncio.create_subprocess_exec', return_value=mock_process):
                # Create dummy voice file
                voice_path = temp_storage / "voice.onnx"
                voice_path.write_bytes(b"dummy voice")
                
                output_path = temp_storage / "output.wav"
                
                # Mock output file creation
                with patch('pathlib.Path.exists', return_value=True):
                    duration = await engine.synthesize_text(
                        text="Test text",
                        voice_path=str(voice_path),
                        output_path=str(output_path)
                    )
                    
                    assert duration is not None
                    assert duration > 0
    
    @pytest.mark.asyncio
    async def test_synthesize_text_empty_text(self, temp_storage):
        """Test synthesis with empty text."""
        with patch('shutil.which', return_value='/usr/local/bin/piper'):
            engine = TTSEngine()
            
            voice_path = temp_storage / "voice.onnx"
            output_path = temp_storage / "output.wav"
            
            with pytest.raises(TTSEngineError, match="Empty text provided"):
                await engine.synthesize_text(
                    text="",
                    voice_path=str(voice_path),
                    output_path=str(output_path)
                )
    
    @pytest.mark.asyncio
    async def test_synthesize_text_voice_not_found(self, temp_storage):
        """Test synthesis with non-existent voice file."""
        with patch('shutil.which', return_value='/usr/local/bin/piper'):
            engine = TTSEngine()
            
            voice_path = temp_storage / "nonexistent.onnx"
            output_path = temp_storage / "output.wav"
            
            with pytest.raises(TTSEngineError, match="Voice model file not found"):
                await engine.synthesize_text(
                    text="Test text",
                    voice_path=str(voice_path),
                    output_path=str(output_path)
                )
    
    def test_estimate_audio_duration(self):
        """Test audio duration estimation."""
        with patch('shutil.which', return_value='/usr/local/bin/piper'):
            engine = TTSEngine()
            
            # Test with known text
            text = "This is a test sentence. This is another sentence!"
            duration = engine._estimate_audio_duration(text, 1.0, 0.35)
            
            assert duration > 0
            
            # Test with speed adjustment
            slow_duration = engine._estimate_audio_duration(text, 1.5, 0.35)
            fast_duration = engine._estimate_audio_duration(text, 0.5, 0.35)
            
            assert slow_duration > duration
            assert fast_duration < duration