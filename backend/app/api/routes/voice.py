"""Voice management endpoints."""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import json
from pathlib import Path

from app.core.config import settings
from app.models.voice import Voice, VoicesListResponse, VoiceMetadata, VoiceTechnicalInfo, VoiceQuality

router = APIRouter()


@router.get("/list", response_model=VoicesListResponse)
async def list_voices():
    """
    List all available voice models with complete metadata.
    
    Returns:
        Complete list of voices with metadata and technical info
    """
    voices_dir = settings.VOICES_BASE_PATH
    available_voices = []
    
    if not voices_dir.exists():
        return VoicesListResponse(
            voices=[],
            count=0,
            default_voice=settings.DEFAULT_VOICE_MODEL
        )
    
    # Scan for .onnx model files
    for model_file in voices_dir.rglob("*.onnx"):
        try:
            # Build Voice object
            voice = await _build_voice_from_model(model_file)
            if voice:
                available_voices.append(voice)
                
        except Exception as e:
            print(f"Warning: Failed to process voice model {model_file}: {e}")
            continue
    
    # Sort voices by language and quality
    available_voices.sort(key=lambda v: (
        v.metadata.language_code,
        v.metadata.gender or "unknown",
        v.technical_info.model_size
    ))
    
    return VoicesListResponse(
        voices=available_voices,
        count=len(available_voices),
        default_voice=settings.DEFAULT_VOICE_MODEL
    )


@router.get("/{voice_id}")
async def get_voice_details(voice_id: str):
    """
    Get detailed information about a specific voice.
    
    Args:
        voice_id: Voice identifier (model name)
        
    Returns:
        Detailed voice information
    """
    voices_dir = settings.VOICES_BASE_PATH
    
    # Find voice model file
    for model_file in voices_dir.rglob("*.onnx"):
        if voice_id in str(model_file):
            try:
                voice = await _build_voice_from_model(model_file)
                if voice and voice.id == voice_id:
                    return voice
            except Exception as e:
                raise HTTPException(500, f"Error loading voice: {str(e)}")
    
    raise HTTPException(404, f"Voice '{voice_id}' not found")


@router.get("/validate/{voice_id}")
async def validate_voice(voice_id: str):
    """
    Validate that a voice model is properly installed and usable.
    
    Args:
        voice_id: Voice identifier to validate
        
    Returns:
        Validation status and any issues found
    """
    voices_dir = settings.VOICES_BASE_PATH
    
    # Find voice model file
    model_file = None
    for candidate in voices_dir.rglob("*.onnx"):
        if voice_id in str(candidate):
            model_file = candidate
            break
    
    if not model_file:
        return {
            "voice_id": voice_id,
            "valid": False,
            "error": "Voice model file not found",
            "issues": ["Model file (.onnx) missing"]
        }
    
    issues = []
    
    # Check model file
    if not model_file.exists():
        issues.append("Model file does not exist")
    elif not model_file.is_file():
        issues.append("Model path is not a file")
    elif model_file.stat().st_size == 0:
        issues.append("Model file is empty")
    
    # Check config file
    config_file = model_file.with_suffix(".onnx.json")
    if not config_file.exists():
        issues.append("Configuration file (.onnx.json) missing")
    elif config_file.stat().st_size == 0:
        issues.append("Configuration file is empty")
    
    # Try to load config
    config_valid = False
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Basic config validation
            required_keys = ["audio", "num_speakers", "sample_rate"]
            missing_keys = [key for key in required_keys if key not in config_data]
            if missing_keys:
                issues.append(f"Config missing required keys: {missing_keys}")
            else:
                config_valid = True
                
        except json.JSONDecodeError:
            issues.append("Configuration file contains invalid JSON")
        except Exception as e:
            issues.append(f"Error reading configuration file: {str(e)}")
    
    return {
        "voice_id": voice_id,
        "valid": len(issues) == 0,
        "model_file": str(model_file),
        "config_file": str(config_file),
        "config_valid": config_valid,
        "issues": issues
    }


async def _build_voice_from_model(model_file: Path) -> Voice:
    """
    Build a Voice object from a model file with metadata.
    
    Args:
        model_file: Path to .onnx model file
        
    Returns:
        Complete Voice object with metadata
    """
    # Generate voice ID from path
    voice_id = model_file.stem
    
    # Default metadata
    metadata = VoiceMetadata(
        name=_format_voice_name(model_file.stem),
        language_code="fr_FR",  # Default
        recommended_usage=["audiobook", "news"]
    )
    
    # Default technical info
    technical_info = VoiceTechnicalInfo(
        sample_rate=22050,
        num_speakers=1,
        model_size=_extract_model_size(model_file.stem)
    )
    
    # Try to load metadata from JSON file
    json_file = model_file.with_suffix(".onnx.json")
    if json_file.exists():
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Extract metadata
            if "language" in json_data:
                lang_info = json_data["language"]
                metadata.language_code = lang_info.get("code", "fr_FR")
            
            if "dataset" in json_data:
                metadata.dataset = json_data["dataset"]
            
            # Extract technical info
            if "audio" in json_data:
                audio_info = json_data["audio"]
                technical_info.sample_rate = audio_info.get("sample_rate", 22050)
                
            if "num_speakers" in json_data:
                technical_info.num_speakers = json_data["num_speakers"]
                
            # Infer gender and usage from dataset name
            dataset_name = metadata.dataset or model_file.stem.lower()
            metadata.gender = _infer_gender(dataset_name)
            metadata.recommended_usage = _infer_usage_from_dataset(dataset_name)
                
        except Exception as e:
            print(f"Warning: Could not parse metadata for {model_file}: {e}")
    
    # Check if files exist and are accessible
    available = (
        model_file.exists() and 
        model_file.is_file() and 
        model_file.stat().st_size > 0
    )
    
    return Voice(
        id=voice_id,
        model_path=str(model_file),
        config_path=str(json_file) if json_file.exists() else str(model_file.with_suffix(".onnx.json")),
        metadata=metadata,
        technical_info=technical_info,
        available=available
    )


def _format_voice_name(stem: str) -> str:
    """Format voice name from file stem."""
    # Example: fr_FR-siwis-low -> Siwis (Low Quality)
    parts = stem.split('-')
    if len(parts) >= 2:
        dataset = parts[1].capitalize()
        quality = parts[2].capitalize() if len(parts) > 2 else "Medium"
        return f"{dataset} ({quality} Quality)"
    return stem.replace('_', ' ').title()


def _extract_model_size(stem: str) -> str:
    """Extract model size from filename."""
    if "low" in stem.lower():
        return "low"
    elif "high" in stem.lower():
        return "high"
    elif "medium" in stem.lower():
        return "medium"
    return "medium"  # default


def _infer_gender(dataset_name: str) -> str:
    """Infer speaker gender from dataset name."""
    dataset_name = dataset_name.lower()
    
    # Known male voice patterns
    male_indicators = ["tom", "bernard", "gilles"]
    # Known female voice patterns  
    female_indicators = ["siwis", "mls", "amy", "jenny"]
    
    for indicator in male_indicators:
        if indicator in dataset_name:
            return "male"
    
    for indicator in female_indicators:
        if indicator in dataset_name:
            return "female"
    
    return "unknown"


def _infer_usage_from_dataset(dataset_name: str) -> List[str]:
    """Infer recommended usage from dataset characteristics."""
    dataset_name = dataset_name.lower()
    usage = ["audiobook", "news"]  # base usage
    
    if "siwis" in dataset_name:
        usage.extend(["storytelling", "education"])
    elif "tom" in dataset_name:
        usage.extend(["storytelling", "entertainment"])
    elif "upmc" in dataset_name:
        usage.extend(["education", "professional"])
    elif "mls" in dataset_name:
        usage.extend(["dialogue", "conversation"])
    elif "bernard" in dataset_name:
        usage.extend(["documentary", "professional"])
    
    return list(set(usage))  # remove duplicates