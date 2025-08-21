"""TTS engine integration using Piper."""

import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.exceptions import TTSError


class PiperTTSEngine:
    """Piper TTS engine integration."""
    
    def __init__(
        self,
        voice_model: Optional[str] = None,
        length_scale: Optional[float] = None,
        noise_scale: Optional[float] = None,
        noise_w: Optional[float] = None,
        sentence_silence: Optional[float] = None,
    ):
        """
        Initialize Piper TTS engine with configuration.
        
        Args:
            voice_model: Path to voice model (.onnx file)
            length_scale: Speech speed (1.0 = normal, 0.9 = faster, 1.1 = slower)
            noise_scale: Voice variation
            noise_w: Additional noise parameter
            sentence_silence: Pause between sentences in seconds
        """
        self.voice_model = voice_model or settings.voice_model
        self.length_scale = length_scale or settings.length_scale
        self.noise_scale = noise_scale or settings.noise_scale
        self.noise_w = noise_w or settings.noise_w
        self.sentence_silence = sentence_silence or settings.sentence_silence
        
        # Validate voice model exists
        if not Path(self.voice_model).exists():
            raise TTSError(f"Voice model not found: {self.voice_model}")
    
    def text_to_wav(self, text: str, output_path: Path) -> None:
        """
        Convert text to WAV audio using Piper CLI.
        
        Args:
            text: Text content to synthesize
            output_path: Path where WAV file will be saved
            
        Raises:
            TTSError: If synthesis fails
        """
        try:
            cmd = [
                "piper",
                "--model", self.voice_model,
                "--output_file", str(output_path),
                "--length_scale", str(self.length_scale),
                "--noise_scale", str(self.noise_scale),
                "--noise_w", str(self.noise_w),
                "--sentence_silence", str(self.sentence_silence),
            ]
            
            # Pass text via stdin (each line = one utterance)
            # Force single utterance per block
            text_input = text.strip() + "\n"
            
            result = subprocess.run(
                cmd,
                input=text_input,
                text=True,
                check=True,
                capture_output=True
            )
            
        except subprocess.CalledProcessError as e:
            raise TTSError(f"Piper TTS failed: {e.stderr}")
        except FileNotFoundError:
            raise TTSError("Piper TTS binary not found in PATH")
    
    @staticmethod
    def is_available() -> bool:
        """Check if Piper TTS is available in system PATH."""
        try:
            subprocess.run(
                ["piper", "--help"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False