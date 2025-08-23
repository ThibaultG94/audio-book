"""Lightweight TTS service for voice previews."""

import subprocess
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.exceptions import TTSError


class PreviewTTSEngine:
    """
    Lightweight TTS engine for generating voice previews.
    Optimized for short text samples and quick generation.
    """
    
    def __init__(
        self,
        voice_model: Optional[str] = None,
        length_scale: Optional[float] = None,
        noise_scale: Optional[float] = None,
        noise_w: Optional[float] = None,
    ):
        """
        Initialize Preview TTS engine.
        
        Args:
            voice_model: Path to voice model (.onnx file)
            length_scale: Speech speed (1.0 = normal, 0.9 = faster, 1.1 = slower)
            noise_scale: Voice variation (0.0-1.0)
            noise_w: Additional noise parameter
        """
        self.voice_model = voice_model or settings.voice_model
        self.length_scale = length_scale or settings.length_scale
        self.noise_scale = noise_scale or settings.noise_scale
        self.noise_w = noise_w or settings.noise_w
        
        # For previews, use minimal sentence silence for faster generation
        self.sentence_silence = 0.1  # Shorter pause than full conversion
        
        # Validate voice model exists
        if not Path(self.voice_model).exists():
            raise TTSError(f"Voice model not found: {self.voice_model}")
    
    def text_to_wav(self, text: str, output_path: Path) -> None:
        """
        Convert short text to WAV audio for preview.
        
        Args:
            text: Text content to synthesize (should be short, <500 chars)
            output_path: Path where WAV file will be saved
            
        Raises:
            TTSError: If synthesis fails
        """
        # Validate text length for preview
        if len(text) > 500:
            raise TTSError("Preview text too long (max 500 characters)")
        
        if not text.strip():
            raise TTSError("Empty text provided for preview")
        
        try:
            # Build Piper command optimized for preview
            cmd = [
                "piper",
                "--model", self.voice_model,
                "--output_file", str(output_path),
                "--length_scale", str(self.length_scale),
                "--noise_scale", str(self.noise_scale),
                "--noise_w", str(self.noise_w),
                "--sentence_silence", str(self.sentence_silence),
            ]
            
            # Clean and prepare text for TTS
            clean_text = self._clean_preview_text(text)
            text_input = clean_text.strip() + "\n"
            
            # Execute Piper TTS
            result = subprocess.run(
                cmd,
                input=text_input,
                text=True,
                check=True,
                capture_output=True,
                timeout=30  # 30 second timeout for previews
            )
            
            # Verify output file was created
            if not output_path.exists() or output_path.stat().st_size == 0:
                raise TTSError("Preview audio generation failed - no output produced")
                
        except subprocess.TimeoutExpired:
            raise TTSError("Preview generation timed out (>30 seconds)")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else "Unknown error"
            raise TTSError(f"Piper TTS failed: {error_msg}")
        except FileNotFoundError:
            raise TTSError("Piper TTS binary not found in PATH")
    
    def _clean_preview_text(self, text: str) -> str:
        """
        Clean text for preview TTS generation.
        
        Args:
            text: Raw text input
            
        Returns:
            Cleaned text suitable for TTS
        """
        import re
        import unicodedata
        
        # Basic Unicode normalization
        text = unicodedata.normalize("NFKD", text)
        text = "".join(c for c in text if not unicodedata.combining(c))
        
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)
        
        # Remove problematic characters for TTS
        text = re.sub(r"[^\w\s\.,!?;:()\-'\"']", " ", text)
        
        # Ensure proper sentence ending
        text = text.strip()
        if text and text[-1] not in ".!?":
            text += "."
        
        return text
    
    @staticmethod
    def is_available() -> bool:
        """
        Check if Piper TTS is available for preview generation.
        
        Returns:
            True if Piper TTS is available, False otherwise
        """
        try:
            subprocess.run(
                ["piper", "--help"],
                capture_output=True,
                check=True,
                timeout=5
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    @staticmethod 
    def get_voice_info(model_path: str) -> dict:
        """
        Get information about a voice model.
        
        Args:
            model_path: Path to voice model file
            
        Returns:
            Dictionary with voice model information
        """
        import json
        
        model_file = Path(model_path)
        json_file = model_file.with_suffix(".onnx.json")
        
        info = {
            "name": model_file.stem,
            "path": str(model_file),
            "exists": model_file.exists()
        }
        
        # Load metadata if available
        if json_file.exists():
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                info.update({
                    "language": metadata.get("language", {}),
                    "dataset": metadata.get("dataset"),
                    "quality": metadata.get("audio", {}).get("quality"),
                    "sample_rate": metadata.get("audio", {}).get("sample_rate"),
                    "num_speakers": metadata.get("num_speakers", 1)
                })
            except Exception:
                pass  # Ignore metadata parsing errors
        
        return info
    
    def estimate_duration(self, text: str) -> float:
        """
        Estimate audio duration for given text.
        
        Args:
            text: Text to estimate duration for
            
        Returns:
            Estimated duration in seconds
        """
        # Rough estimation: ~150 words per minute for average speech
        # Adjusted by length_scale
        word_count = len(text.split())
        base_duration = (word_count / 150) * 60  # Base duration in seconds
        adjusted_duration = base_duration / self.length_scale
        
        # Add small buffer for sentence pauses
        return max(1.0, adjusted_duration + 0.5)