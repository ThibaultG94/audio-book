"""Enhanced voice management service with metadata and recommendations."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from app.core.config import settings


class VoiceGender(str, Enum):
    """Voice gender enumeration."""
    FEMALE = "female"
    MALE = "male"
    MULTI = "multi"
    NEUTRAL = "neutral"


class VoiceQuality(str, Enum):
    """Voice quality levels."""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"


class UsageType(str, Enum):
    """Voice usage recommendations."""
    AUDIOBOOK = "audiobook"
    NEWS = "news"
    STORYTELLING = "storytelling"
    EDUCATIONAL = "educational"
    DOCUMENTARY = "documentary"
    PROFESSIONAL = "professional"
    ENTERTAINMENT = "entertainment"
    DIALOGUE = "dialogue"


@dataclass
class VoiceSpeaker:
    """Voice speaker characteristics."""
    gender: VoiceGender
    age_range: str  # young, adult, senior
    voice_style: str  # neutral, expressive, warm, authoritative, calm
    accent: str = "standard"
    available_speakers: Optional[Dict[str, Any]] = None


@dataclass  
class VoiceTechnical:
    """Technical voice specifications."""
    quality: VoiceQuality
    sample_rate: int
    dataset: str
    file_size_mb: int
    processing_speed: str  # fast, medium, slow


@dataclass
class VoiceMetadata:
    """Complete voice metadata."""
    name: str
    display_name: str
    language: Dict[str, str]
    speaker: VoiceSpeaker
    technical: VoiceTechnical
    recommended_usage: List[UsageType]
    description: str
    best_for: str
    avatar: str
    color: str
    model_path: str


class VoiceManager:
    """Enhanced voice management with metadata and recommendations."""
    
    def __init__(self):
        self.metadata_file = settings.voices_dir / "voice_metadata.json"
        self.voices_metadata: Dict[str, VoiceMetadata] = {}
        self.load_metadata()
    
    def load_metadata(self) -> None:
        """Load voice metadata from JSON file with fallback generation."""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Parse metadata into dataclass objects
                for model_path, meta in data.get("voices", {}).items():
                    self.voices_metadata[model_path] = self._parse_voice_metadata(model_path, meta)
                    
                print(f"✅ Loaded metadata for {len(self.voices_metadata)} voices")
            else:
                print("⚠️  Voice metadata not found, generating from available models...")
                self.generate_metadata_from_models()
                
        except Exception as e:
            print(f"❌ Error loading voice metadata: {e}")
            self.generate_metadata_from_models()
    
    def _parse_voice_metadata(self, model_path: str, meta: Dict[str, Any]) -> VoiceMetadata:
        """Parse dictionary metadata into dataclass."""
        return VoiceMetadata(
            name=meta["name"],
            display_name=meta["display_name"],
            language=meta["language"],
            speaker=VoiceSpeaker(
                gender=VoiceGender(meta["speaker"]["gender"]),
                age_range=meta["speaker"]["age_range"],
                voice_style=meta["speaker"]["voice_style"],
                accent=meta["speaker"].get("accent", "standard"),
                available_speakers=meta["speaker"].get("available_speakers")
            ),
            technical=VoiceTechnical(
                quality=VoiceQuality(meta["technical"]["quality"]),
                sample_rate=meta["technical"]["sample_rate"],
                dataset=meta["technical"]["dataset"],
                file_size_mb=meta["technical"]["file_size_mb"],
                processing_speed=meta["technical"]["processing_speed"]
            ),
            recommended_usage=[UsageType(usage) for usage in meta["recommended_usage"]],
            description=meta["description"],
            best_for=meta["best_for"],
            avatar=meta["avatar"],
            color=meta["color"],
            model_path=model_path
        )
    
    def generate_metadata_from_models(self) -> None:
        """Generate basic metadata from available .onnx files."""
        if not settings.voices_dir.exists():
            return
            
        for onnx_file in settings.voices_dir.rglob("*.onnx"):
            relative_path = str(onnx_file.relative_to(Path.cwd()))
            
            # Generate basic metadata from file path and JSON metadata
            metadata = self._generate_basic_metadata(onnx_file, relative_path)
            self.voices_metadata[relative_path] = metadata
            
        self.save_metadata()
    
    def _generate_basic_metadata(self, onnx_file: Path, relative_path: str) -> VoiceMetadata:
        """Generate basic metadata for a voice model."""
        json_file = onnx_file.with_suffix(".onnx.json")
        
        # Parse existing JSON metadata if available
        tech_metadata = {}
        if json_file.exists():
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    tech_metadata = json.load(f)
            except Exception:
                pass
        
        # Extract info from path (e.g., fr_FR-siwis-medium.onnx)
        filename = onnx_file.stem  # fr_FR-siwis-medium
        parts = filename.split('-')
        
        dataset = parts[1] if len(parts) > 1 else "unknown"
        quality = parts[2] if len(parts) > 2 else "medium"
        
        # Infer characteristics from dataset name
        gender, avatar, color = self._infer_voice_characteristics(dataset, filename)
        
        file_size = onnx_file.stat().st_size // (1024 * 1024) if onnx_file.exists() else 0
        
        return VoiceMetadata(
            name=dataset.title(),
            display_name=f"{dataset.title()} ({quality.title()})",
            language={
                "code": "fr_FR",
                "name_english": "French", 
                "name_native": "Français"
            },
            speaker=VoiceSpeaker(
                gender=gender,
                age_range="adult",
                voice_style="neutral",
                accent="standard"
            ),
            technical=VoiceTechnical(
                quality=VoiceQuality(quality.lower()) if quality.lower() in ["low", "medium", "high"] else VoiceQuality.MEDIUM,
                sample_rate=tech_metadata.get("audio", {}).get("sample_rate", 22050),
                dataset=dataset,
                file_size_mb=file_size,
                processing_speed="medium"
            ),
            recommended_usage=[UsageType.AUDIOBOOK, UsageType.NEWS],
            description=f"Voix {gender} {dataset}, qualité {quality}",
            best_for="Usage général",
            avatar=avatar,
            color=color,
            model_path=relative_path
        )
    
    def _infer_voice_characteristics(self, dataset: str, filename: str) -> tuple[VoiceGender, str, str]:
        """Infer voice gender and visual characteristics from dataset name."""
        dataset_lower = dataset.lower()
        filename_lower = filename.lower()
        
        # Known male voice datasets/names
        male_indicators = ["tom", "bernard", "gilles", "pierre", "male"]
        # Known female voice datasets/names  
        female_indicators = ["siwis", "jessica", "marie", "female"]
        # Multi-speaker datasets
        multi_indicators = ["upmc"]
        
        if any(indicator in dataset_lower or indicator in filename_lower for indicator in male_indicators):
            return VoiceGender.MALE, "👨‍💼", "#059669"
        elif any(indicator in dataset_lower for indicator in multi_indicators):
            return VoiceGender.MULTI, "👫", "#10B981"
        else:
            # Default to female for most French TTS models
            return VoiceGender.FEMALE, "👩‍💼", "#3B82F6"
    
    def get_all_voices(self) -> List[VoiceMetadata]:
        """Get all available voices with metadata."""
        return list(self.voices_metadata.values())
    
    def get_voice_by_path(self, model_path: str) -> Optional[VoiceMetadata]:
        """Get voice metadata by model path."""
        return self.voices_metadata.get(model_path)
    
    def filter_voices(
        self,
        gender: Optional[VoiceGender] = None,
        quality: Optional[VoiceQuality] = None, 
        usage: Optional[UsageType] = None,
        max_file_size_mb: Optional[int] = None
    ) -> List[VoiceMetadata]:
        """Filter voices by criteria."""
        filtered = []
        
        for voice in self.voices_metadata.values():
            # Gender filter
            if gender and voice.speaker.gender != gender:
                continue
                
            # Quality filter  
            if quality and voice.technical.quality != quality:
                continue
                
            # Usage filter
            if usage and usage not in voice.recommended_usage:
                continue
                
            # File size filter
            if max_file_size_mb and voice.technical.file_size_mb > max_file_size_mb:
                continue
                
            filtered.append(voice)
            
        return filtered
    
    def get_recommendations_for_usage(self, usage: UsageType) -> List[VoiceMetadata]:
        """Get recommended voices for specific usage."""
        return self.filter_voices(usage=usage)
    
    def get_best_quality_voices(self) -> List[VoiceMetadata]:
        """Get highest quality voices available."""
        return sorted(
            self.voices_metadata.values(),
            key=lambda v: {"high": 3, "medium": 2, "low": 1}.get(v.technical.quality.value, 0),
            reverse=True
        )
    
    def get_fastest_processing_voices(self) -> List[VoiceMetadata]:
        """Get voices optimized for fast processing."""
        return sorted(
            self.voices_metadata.values(), 
            key=lambda v: {"fast": 3, "medium": 2, "slow": 1}.get(v.technical.processing_speed, 1),
            reverse=True
        )
    
    def get_voice_statistics(self) -> Dict[str, Any]:
        """Get statistics about available voices."""
        voices = list(self.voices_metadata.values())
        
        if not voices:
            return {"total": 0}
            
        return {
            "total": len(voices),
            "by_gender": {
                gender.value: len([v for v in voices if v.speaker.gender == gender])
                for gender in VoiceGender
            },
            "by_quality": {
                quality.value: len([v for v in voices if v.technical.quality == quality])
                for quality in VoiceQuality  
            },
            "total_size_mb": sum(v.technical.file_size_mb for v in voices),
            "average_size_mb": sum(v.technical.file_size_mb for v in voices) / len(voices),
            "available_languages": list(set(v.language["code"] for v in voices))
        }
    
    def save_metadata(self) -> None:
        """Save current metadata to JSON file."""
        try:
            # Convert dataclasses back to dict for JSON serialization
            voices_dict = {}
            for path, voice in self.voices_metadata.items():
                voices_dict[path] = {
                    "name": voice.name,
                    "display_name": voice.display_name,
                    "language": voice.language,
                    "speaker": {
                        "gender": voice.speaker.gender.value,
                        "age_range": voice.speaker.age_range,
                        "voice_style": voice.speaker.voice_style,
                        "accent": voice.speaker.accent,
                        **({"available_speakers": voice.speaker.available_speakers} 
                           if voice.speaker.available_speakers else {})
                    },
                    "technical": {
                        "quality": voice.technical.quality.value,
                        "sample_rate": voice.technical.sample_rate,
                        "dataset": voice.technical.dataset,
                        "file_size_mb": voice.technical.file_size_mb,
                        "processing_speed": voice.technical.processing_speed
                    },
                    "recommended_usage": [usage.value for usage in voice.recommended_usage],
                    "description": voice.description,
                    "best_for": voice.best_for,
                    "avatar": voice.avatar,
                    "color": voice.color
                }
            
            data = {
                "version": "1.1.0",
                "voices": voices_dict
            }
            
            # Ensure directory exists
            self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            print(f"✅ Saved metadata for {len(voices_dict)} voices to {self.metadata_file}")
            
        except Exception as e:
            print(f"❌ Error saving voice metadata: {e}")


# Global voice manager instance
voice_manager = VoiceManager()