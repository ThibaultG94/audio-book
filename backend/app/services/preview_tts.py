"""Lightweight TTS service for voice previews with path validation."""

import subprocess
import os
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
        Initialize Preview TTS engine with path validation.
        
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
        
        # Validate and resolve voice model path
        self.voice_model_path = self._resolve_voice_model_path()
    
    def _resolve_voice_model_path(self) -> Path:
        """
        Resolve and validate voice model path.
        
        Returns:
            Absolute path to voice model
            
        Raises:
            TTSError: If voice model not found
        """
        # Try different path combinations
        possible_paths = [
            Path(self.voice_model),  # Direct path as given
            Path("backend") / self.voice_model,  # With backend/ prefix
            Path.cwd() / self.voice_model,  # From current working directory
            Path.cwd() / "backend" / self.voice_model,  # From project root
        ]
        
        print(f"🔍 Looking for voice model: {self.voice_model}")
        print(f"📁 Current working directory: {Path.cwd()}")
        
        for path in possible_paths:
            abs_path = path.resolve()
            print(f"  Trying: {abs_path}")
            if abs_path.exists():
                print(f"✅ Found voice model at: {abs_path}")
                return abs_path
        
        # If not found, try to find ANY .onnx file in voices directory
        voices_dirs = [
            Path("voices"),
            Path("backend/voices"),
            Path.cwd() / "voices",
            Path.cwd() / "backend/voices"
        ]
        
        for voices_dir in voices_dirs:
            if voices_dir.exists():
                print(f"📂 Scanning voices directory: {voices_dir}")
                onnx_files = list(voices_dir.rglob("*.onnx"))
                if onnx_files:
                    print(f"🎤 Available voice models:")
                    for onnx_file in onnx_files:
                        print(f"  - {onnx_file}")
                    
                    # Use the first available model
                    selected_model = onnx_files[0]
                    print(f"⚡ Auto-selecting: {selected_model}")
                    return selected_model
        
        # Generate detailed error message
        error_msg = f"Voice model not found: {self.voice_model}\n"
        error_msg += f"Current directory: {Path.cwd()}\n"
        error_msg += "Searched paths:\n"
        for path in possible_paths:
            error_msg += f"  - {path.resolve()} (exists: {path.exists()})\n"
        
        raise TTSError(error_msg)
    
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
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Build Piper command optimized for preview
            cmd = [
                "piper",
                "--model", str(self.voice_model_path),  # Use resolved absolute path
                "--output_file", str(output_path),
                "--length_scale", str(self.length_scale),
                "--noise_scale", str(self.noise_scale),
                "--noise_w", str(self.noise_w),
                "--sentence_silence", str(self.sentence_silence),
            ]
            
            # Clean and prepare text for TTS
            clean_text = self._clean_preview_text(text)
            text_input = clean_text.strip() + "\n"
            
            print(f"🎤 Generating preview with command: {' '.join(cmd)}")
            print(f"📝 Input text: {clean_text[:50]}...")
            
            # Execute Piper TTS
            result = subprocess.run(
                cmd,
                input=text_input,
                text=True,
                check=True,
                capture_output=True,
                timeout=30  # 30 second timeout for previews
            )
            
            print(f"✅ Piper stdout: {result.stdout}")
            if result.stderr:
                print(f"⚠️  Piper stderr: {result.stderr}")
            
            # Verify output file was created
            if not output_path.exists() or output_path.stat().st_size == 0:
                raise TTSError("Preview audio generation failed - no output produced")
            
            print(f"🎵 Preview generated: {output_path} ({output_path.stat().st_size} bytes)")
                
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
    def find_voice_models() -> list[Path]:
        """
        Find all available voice models in the system.
        
        Returns:
            List of paths to .onnx voice model files
        """
        voice_models = []
        search_dirs = [
            Path("voices"),
            Path("backend/voices"),
            Path.cwd() / "voices",
            Path.cwd() / "backend/voices"
        ]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                voice_models.extend(search_dir.rglob("*.onnx"))
        
        return list(set(voice_models))  # Remove duplicates