"""TTS Engine service for audio generation."""

import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

from app.core.config import settings  # Fixed import

logger = logging.getLogger(__name__)


class TTSEngine:
    """TTS Engine using Piper for voice synthesis."""
    
    def __init__(self):
        self.piper_executable = "piper"
        
    async def synthesize(
        self,
        text: str,
        voice_model_path: str,
        length_scale: float = 1.0,
        noise_scale: float = 0.667,
        noise_w: float = 0.8,
        sentence_silence: float = 0.35
    ) -> bytes:
        """Synthesize text to audio using Piper.
        
        Args:
            text: Text to synthesize
            voice_model_path: Path to voice model file
            length_scale: Speech speed
            noise_scale: Voice expressiveness
            noise_w: Phonetic variation
            sentence_silence: Pause between sentences
            
        Returns:
            Audio data as bytes
        """
        try:
            cmd = [
                self.piper_executable,
                "--model", voice_model_path,
                "--output_file", "-",  # Output to stdout
                "--length-scale", str(length_scale),
                "--noise-scale", str(noise_scale),
                "--noise-w", str(noise_w),
                "--sentence-silence", str(sentence_silence)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate(input=text.encode('utf-8'))
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                raise RuntimeError(f"Piper synthesis failed: {error_msg}")
            
            return stdout
            
        except FileNotFoundError:
            logger.error("Piper executable not found")
            raise RuntimeError("Piper TTS is not installed or not in PATH")
        except Exception as e:
            logger.error(f"TTS synthesis failed: {str(e)}")
            raise
    
    async def estimate_duration(
        self,
        text: str,
        length_scale: float = 1.0,
        sentence_silence: float = 0.35
    ) -> float:
        """Estimate audio duration for given text.
        
        Args:
            text: Text to estimate
            length_scale: Speech speed factor
            sentence_silence: Pause between sentences
            
        Returns:
            Estimated duration in seconds
        """
        # Rough estimation: ~150 words per minute at normal speed
        word_count = len(text.split())
        base_duration = (word_count / 150) * 60  # seconds
        
        # Adjust for speech speed
        adjusted_duration = base_duration * length_scale
        
        # Add sentence pauses
        sentence_count = text.count('.') + text.count('!') + text.count('?')
        pause_duration = sentence_count * sentence_silence
        
        return adjusted_duration + pause_duration
    
    async def get_voice_info(self, voice_path: str) -> dict:
        """Get information about a voice model.
        
        Args:
            voice_path: Path to voice model file
            
        Returns:
            dict: Voice information from Piper
        """
        try:
            cmd = [self.piper_executable, "--model", voice_path, "--output_file", "-"]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send empty text to get voice info
            stdout, stderr = await process.communicate(b"")
            
            # Parse voice information from stderr (Piper outputs info there)
            info_text = stderr.decode('utf-8')
            
            # Extract relevant information
            info = {
                "model_path": voice_path,
                "is_available": Path(voice_path).exists(),
                "raw_info": info_text
            }
            
            return info
            
        except Exception as e:
            logger.warning(f"Failed to get voice info for {voice_path}: {e}")
            return {
                "model_path": voice_path,
                "is_available": False,
                "error": str(e)
            }