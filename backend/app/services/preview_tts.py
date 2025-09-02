"""Preview TTS service for quick voice testing."""

import logging
import subprocess
from pathlib import Path
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class PreviewTTSService:
    """Service for generating quick TTS previews."""
    
    def __init__(self):
        self.piper_executable = "piper"  # Assuming piper is in PATH
        
    def generate_preview(
        self,
        text: str,
        voice_model: str,
        output_path: str,
        length_scale: float = 1.0,
        noise_scale: float = 0.667,
        noise_w: float = 0.8,
        sentence_silence: float = 0.35
    ) -> bool:
        """Generate a preview audio file.
        
        Args:
            text: Text to synthesize
            voice_model: Path to voice model
            output_path: Path for output audio file
            length_scale: Speech speed
            noise_scale: Voice expressiveness
            noise_w: Phonetic variation
            sentence_silence: Pause between sentences
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Build piper command
            cmd = [
                self.piper_executable,
                "--model", voice_model,
                "--output_file", output_path,
                "--length-scale", str(length_scale),
                "--noise-scale", str(noise_scale),
                "--noise-w", str(noise_w),
                "--sentence-silence", str(sentence_silence)
            ]
            
            # Run piper with text as input
            result = subprocess.run(
                cmd,
                input=text.encode('utf-8'),
                capture_output=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"Piper failed: {result.stderr.decode('utf-8')}")
                return False
            
            # Check if output file was created
            if not Path(output_path).exists():
                logger.error(f"Output file not created: {output_path}")
                return False
            
            logger.info(f"Preview generated successfully: {output_path}")
            return True
            
        except FileNotFoundError:
            logger.error("Piper executable not found. Make sure it's installed and in PATH")
            return False
        except Exception as e:
            logger.error(f"Preview generation failed: {str(e)}")
            return False