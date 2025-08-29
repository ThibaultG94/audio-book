"""TTS Engine service using Piper for audio synthesis."""

import asyncio
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class TTSEngineError(Exception):
    """Custom exception for TTS engine errors."""
    pass


class TTSEngine:
    """Text-to-Speech engine using Piper."""
    
    def __init__(self):
        self.settings = get_settings()
        self.piper_executable = self._find_piper_executable()
    
    def _find_piper_executable(self) -> str:
        """Find Piper executable in system PATH or raise error."""
        piper_path = shutil.which(self.settings.PIPER_EXECUTABLE)
        if not piper_path:
            # Try common installation paths
            common_paths = [
                "/usr/local/bin/piper",
                "/usr/bin/piper",
                "./piper",  # Local installation
            ]
            
            for path in common_paths:
                if Path(path).exists():
                    piper_path = path
                    break
        
        if not piper_path:
            raise TTSEngineError(
                f"Piper executable not found. Please install Piper TTS or set PIPER_EXECUTABLE environment variable."
            )
        
        logger.info(f"Using Piper executable: {piper_path}")
        return piper_path
    
    async def synthesize_text(
        self,
        text: str,
        voice_path: str,
        output_path: str,
        length_scale: float = 1.0,
        noise_scale: float = 0.667,
        noise_w: float = 0.8,
        sentence_silence: float = 0.35
    ) -> Optional[float]:
        """Synthesize text to audio using Piper TTS.
        
        Args:
            text: Text to synthesize
            voice_path: Path to voice model (.onnx file)
            output_path: Output audio file path
            length_scale: Speech speed (1.0 = normal)
            noise_scale: Voice variation amount
            noise_w: Phoneme width variation
            sentence_silence: Pause between sentences (seconds)
            
        Returns:
            Optional[float]: Audio duration in seconds, or None if failed
            
        Raises:
            TTSEngineError: If synthesis fails
        """
        try:
            # Validate inputs
            if not text.strip():
                raise TTSEngineError("Empty text provided")
            
            # Limit text size to prevent memory issues (max 1000 chars per chunk)
            if len(text) > 1000:
                logger.warning(f"Text chunk is large ({len(text)} chars), this might cause memory issues")
                # Truncate if too large to prevent Piper crash
                text = text[:1000] + "..."
            
            voice_file = Path(voice_path)
            logger.info(f"Looking for voice model at: {voice_file.absolute()}")
            if not voice_file.exists():
                logger.error(f"Voice model file not found: {voice_file.absolute()}")
                # Try to find similar files for debugging
                parent_dir = voice_file.parent
                if parent_dir.exists():
                    logger.error(f"Files in {parent_dir}: {list(parent_dir.iterdir())}")
                raise TTSEngineError(f"Voice model file not found: {voice_path}")
            
            # Ensure output directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare Piper command with resource limits
            cmd = [
                "timeout", "60s",  # Hard timeout at 60 seconds
                self.piper_executable,
                "--model", str(voice_file),
                "--output_file", str(output_file),
                "--length_scale", str(length_scale),
                "--noise_scale", str(noise_scale),
                "--noise_w", str(noise_w),
                "--sentence_silence", str(sentence_silence)
            ]
            
            logger.debug(f"Running Piper command: {' '.join(cmd)}")
            
            # Run Piper synthesis with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send text to Piper via stdin with timeout (60 seconds max)
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(text.encode('utf-8')), 
                    timeout=60.0
                )
            except asyncio.TimeoutError:
                logger.error(f"Piper synthesis timed out after 60 seconds")
                process.kill()
                await process.wait()
                raise TTSEngineError("TTS synthesis timed out")
            
            # Check for errors
            if process.returncode != 0:
                stderr_text = stderr.decode('utf-8') if stderr else ""
                stdout_text = stdout.decode('utf-8') if stdout else ""
                error_msg = stderr_text or stdout_text or f"Piper exited with code {process.returncode}"
                logger.error(f"Piper synthesis failed: {error_msg}")
                logger.error(f"Command was: {' '.join(cmd)}")
                logger.error(f"Return code: {process.returncode}")
                logger.error(f"STDERR: {stderr_text}")
                logger.error(f"STDOUT: {stdout_text}")
                raise TTSEngineError(f"TTS synthesis failed: {error_msg}")
            
            # Verify output file was created
            if not output_file.exists():
                raise TTSEngineError("Output audio file was not created")
            
            # Calculate audio duration (approximate)
            duration = self._estimate_audio_duration(text, length_scale, sentence_silence)
            
            logger.info(f"TTS synthesis completed: {output_path} ({duration:.2f}s)")
            return duration
            
        except TTSEngineError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in TTS synthesis: {e}")
            raise TTSEngineError(f"TTS synthesis failed: {str(e)}")
    
    def _estimate_audio_duration(
        self, 
        text: str, 
        length_scale: float, 
        sentence_silence: float
    ) -> float:
        """Estimate audio duration based on text length and parameters.
        
        This is an approximation - actual duration may vary.
        """
        # Rough estimation: ~150 words per minute for normal speech
        words = len(text.split())
        base_duration = (words / 150) * 60  # Convert to seconds
        
        # Adjust for speech speed
        adjusted_duration = base_duration * length_scale
        
        # Add sentence pauses (rough estimate)
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