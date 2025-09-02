"""Voice model management service."""

import logging
import json
from pathlib import Path
from typing import List, Dict, Optional, Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class VoiceManager:
    """Service for managing and discovering voice models."""
    
    def __init__(self):
        self.voices_base_path = settings.VOICES_BASE_PATH
        self._voice_cache = None
        
    def discover_voices(self) -> List[Dict[str, Any]]:
        """Discover all available voice models.
        
        Returns:
            List of voice model information
        """
        voices = []
        
        # Ensure voices directory exists
        if not self.voices_base_path.exists():
            logger.warning(f"Voices directory does not exist: {self.voices_base_path}")
            self.voices_base_path.mkdir(parents=True, exist_ok=True)
            return voices
        
        # Search for .onnx files recursively
        for onnx_file in self.voices_base_path.rglob("*.onnx"):
            try:
                # Skip if it's not a file
                if not onnx_file.is_file():
                    continue
                    
                # Look for corresponding JSON config
                json_config = onnx_file.with_suffix(".onnx.json")
                
                voice_info = {
                    "model_path": str(onnx_file),
                    "config_path": str(json_config) if json_config.exists() else None,
                    "name": onnx_file.stem.replace(".onnx", ""),
                    "available": True
                }
                
                # Try to load metadata from JSON config
                if json_config.exists():
                    try:
                        with open(json_config, 'r') as f:
                            config = json.load(f)
                            voice_info.update({
                                "language": config.get("language", {}).get("code", "unknown"),
                                "sample_rate": config.get("audio", {}).get("sample_rate", 22050),
                                "quality": config.get("audio", {}).get("quality", "medium"),
                                "dataset": config.get("dataset", "unknown"),
                                "num_speakers": config.get("num_speakers", 1)
                            })
                    except Exception as e:
                        logger.warning(f"Failed to parse config for {onnx_file}: {e}")
                
                # Extract info from path structure (e.g., fr/fr_FR/siwis/low/)
                parts = onnx_file.relative_to(self.voices_base_path).parts
                if len(parts) >= 2:
                    voice_info["language_family"] = parts[0]  # e.g., "fr"
                    if len(parts) >= 3:
                        voice_info["locale"] = parts[1]  # e.g., "fr_FR"
                    if len(parts) >= 4:
                        voice_info["dataset"] = parts[2]  # e.g., "siwis"
                    if len(parts) >= 5:
                        voice_info["quality"] = parts[3]  # e.g., "low"
                
                voices.append(voice_info)
                logger.info(f"Discovered voice: {voice_info['name']} at {onnx_file}")
                
            except Exception as e:
                logger.error(f"Error processing voice model {onnx_file}: {e}")
                continue
        
        # Sort by name
        voices.sort(key=lambda v: v.get("name", ""))
        
        logger.info(f"Discovered {len(voices)} voice models")
        return voices
    
    def list_voices(self, language: Optional[str] = None, quality: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available voices with optional filtering.
        
        Args:
            language: Filter by language code (e.g., "fr_FR")
            quality: Filter by quality level (e.g., "low", "medium", "high")
            
        Returns:
            Filtered list of voices
        """
        # Use cache if available
        if self._voice_cache is None:
            self._voice_cache = self.discover_voices()
        
        voices = self._voice_cache.copy()
        
        # Apply filters
        if language:
            voices = [v for v in voices if v.get("language") == language or v.get("locale") == language]
        
        if quality:
            voices = [v for v in voices if v.get("quality") == quality]
        
        return voices
    
    def get_voice(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """Get specific voice information.
        
        Args:
            voice_id: Voice identifier (name or path)
            
        Returns:
            Voice information or None if not found
        """
        voices = self.list_voices()
        
        for voice in voices:
            if voice["name"] == voice_id or voice["model_path"] == voice_id:
                return voice
        
        # Try to find by partial path match
        for voice in voices:
            if voice_id in voice["model_path"]:
                return voice
        
        return None
    
    def validate_voice(self, voice_path: str) -> Dict[str, Any]:
        """Validate a voice model.
        
        Args:
            voice_path: Path to voice model
            
        Returns:
            Validation results
        """
        result = {
            "valid": False,
            "model_file": voice_path,
            "issues": []
        }
        
        model_path = Path(voice_path)
        
        # Check if model file exists
        if not model_path.exists():
            result["issues"].append(f"Model file not found: {voice_path}")
            return result
        
        # Check file size
        if model_path.stat().st_size == 0:
            result["issues"].append("Model file is empty")
            return result
        
        # Check for config file
        config_path = model_path.with_suffix(".onnx.json")
        if not config_path.exists():
            result["issues"].append("Config file not found (optional)")
        else:
            # Try to parse config
            try:
                with open(config_path, 'r') as f:
                    json.load(f)
                result["config_valid"] = True
            except Exception as e:
                result["issues"].append(f"Invalid config file: {e}")
                result["config_valid"] = False
        
        # If no critical issues, mark as valid
        if not any("not found" in issue or "empty" in issue for issue in result["issues"]):
            result["valid"] = True
        
        return result
    
    def get_default_voice(self) -> Optional[str]:
        """Get the default voice model path.
        
        Returns:
            Path to default voice model or None
        """
        # Try configured default
        if settings.DEFAULT_VOICE_MODEL:
            voice = self.get_voice(settings.DEFAULT_VOICE_MODEL)
            if voice:
                return voice["model_path"]
        
        # Fall back to first available voice
        voices = self.list_voices()
        if voices:
            return voices[0]["model_path"]
        
        return None
    
    def refresh_cache(self):
        """Refresh the voice cache."""
        self._voice_cache = None
        self.list_voices()  # This will repopulate the cache