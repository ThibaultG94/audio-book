"""Enhanced TTS preview endpoints with all Piper parameters."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import subprocess
import shutil
import os

from app.services.preview_tts import PreviewTTSEngine
from app.core.config import settings
from app.core.exceptions import TTSError

router = APIRouter()

class EnhancedPreviewRequest(BaseModel):
    """Enhanced request for TTS preview with all parameters."""
    text: str = Field(..., min_length=1, max_length=500, description="Text to synthesize (max 500 chars)")
    voice_model: Optional[str] = Field(default=None, description="Voice model path")
    
    # Core TTS parameters
    length_scale: Optional[float] = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed (0.5=fast, 2.0=slow)")
    noise_scale: Optional[float] = Field(default=0.667, ge=0.0, le=1.0, description="Voice expressivity (0=monotone, 1=expressive)")
    noise_w: Optional[float] = Field(default=0.8, ge=0.0, le=1.0, description="Pitch stability (0=stable, 1=variable)")
    sentence_silence: Optional[float] = Field(default=0.35, ge=0.1, le=2.0, description="Pause between sentences (seconds)")

class VoiceModelInfo(BaseModel):
    """Voice model information."""
    model_path: str
    name: str
    full_path: str
    language: Optional[Dict[str, Any]] = None
    dataset: Optional[str] = None
    quality: Optional[str] = None
    sample_rate: Optional[int] = None
    file_size_mb: Optional[float] = None
    recommended_usage: List[str] = Field(default_factory=lambda: ["audiobook", "news"])

class EnhancedPreviewResponse(BaseModel):
    """Enhanced response with detailed info."""
    preview_id: str
    text: str
    audio_url: str
    duration_estimate: float
    voice_model: str
    parameters: Dict[str, float]
    voice_info: Optional[VoiceModelInfo] = None

class VoicesListResponse(BaseModel):
    """Response with all available voices."""
    voices: List[VoiceModelInfo]
    default_voice: str
    count: int
    recommendations: Dict[str, str]

@router.post("/tts", response_model=EnhancedPreviewResponse)
async def generate_enhanced_preview(request: EnhancedPreviewRequest):
    """
    Generate TTS preview with full parameter control.
    
    Args:
        request: Enhanced preview request with all TTS parameters
        
    Returns:
        Preview response with detailed parameter info
    """
    try:
        # Initialize preview engine with all parameters
        preview_engine = PreviewTTSEngine(
            voice_model=request.voice_model,
            length_scale=request.length_scale,
            noise_scale=request.noise_scale,
            noise_w=request.noise_w,
            sentence_silence=request.sentence_silence
        )
        
        # Generate unique preview ID
        preview_id = str(uuid.uuid4())
        
        # Create preview audio file
        preview_path = settings.outputs_dir / "previews" / f"{preview_id}.wav"
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate audio
        preview_engine.text_to_wav(request.text, preview_path)
        
        # Calculate estimated duration (accounting for speed)
        word_count = len(request.text.split())
        base_duration = (word_count / 150) * 60  # ~150 words/minute baseline
        actual_duration = base_duration * request.length_scale + (request.sentence_silence * request.text.count('.'))
        
        # Get voice model info
        voice_info = await get_voice_model_info(preview_engine.voice_model_path)
        
        return EnhancedPreviewResponse(
            preview_id=preview_id,
            text=request.text,
            audio_url=f"/api/preview/audio/{preview_id}",
            duration_estimate=round(actual_duration, 2),
            voice_model=str(preview_engine.voice_model_path),
            parameters={
                "length_scale": request.length_scale,
                "noise_scale": request.noise_scale,
                "noise_w": request.noise_w,
                "sentence_silence": request.sentence_silence
            },
            voice_info=voice_info
        )
        
    except TTSError as e:
        raise HTTPException(500, f"TTS generation failed: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Preview generation failed: {str(e)}")

@router.get("/voices", response_model=VoicesListResponse)
async def list_enhanced_voices():
    """
    List all available voice models with detailed metadata.
    
    Returns:
        Comprehensive list of voices with recommendations
    """
    voices_dir = settings.voices_dir
    available_voices = []
    
    if voices_dir.exists():
        # Scan for .onnx model files
        for model_file in voices_dir.rglob("*.onnx"):
            try:
                voice_info = await get_voice_model_info(model_file)
                
                # CRITICAL FIX: Ensure recommended_usage is always a non-empty array
                if not voice_info.recommended_usage:
                    # Infer usage based on voice characteristics
                    voice_info.recommended_usage = _infer_recommended_usage(voice_info)
                
                available_voices.append(voice_info)
                
            except Exception as e:
                print(f"Warning: Failed to process voice model {model_file}: {e}")
                continue
    
    # Sort by quality and language
    available_voices.sort(key=lambda v: (
        v.language.get("name_english", "zzz") if v.language else "zzz",
        v.quality or "medium",
        v.name
    ))
    
    # Generate recommendations based on use cases
    recommendations = {
        "fastest": _find_best_voice(available_voices, "speed"),
        "highest_quality": _find_best_voice(available_voices, "quality"),
        "most_natural": _find_best_voice(available_voices, "natural"),
        "french_best": _find_best_voice(available_voices, "french")
    }
    
    return VoicesListResponse(
        voices=available_voices,
        default_voice=settings.voice_model,
        count=len(available_voices),
        recommendations=recommendations
    )


def _find_best_voice(voices: List[VoiceModelInfo], criteria: str) -> str:
    """Find best voice model based on criteria."""
    if not voices:
        return "No voices available"
    
    if criteria == "speed":
        # Prefer low quality for speed
        speed_voices = [v for v in voices if v.quality == "low"]
        return speed_voices[0].model_path if speed_voices else voices[0].model_path
    
    elif criteria == "quality":
        # Prefer high quality
        quality_voices = [v for v in voices if v.quality == "high"]
        return quality_voices[0].model_path if quality_voices else voices[0].model_path
    
    elif criteria == "natural":
        # Prefer medium quality as good balance
        natural_voices = [v for v in voices if v.quality == "medium"]
        return natural_voices[0].model_path if natural_voices else voices[0].model_path
    
    elif criteria == "french":
        # Prefer French voices
        french_voices = [v for v in voices if v.language and "fr" in v.language.get("code", "").lower()]
        return french_voices[0].model_path if french_voices else voices[0].model_path
    
    return voices[0].model_path

@router.get("/audio/{preview_id}")
async def get_preview_audio(preview_id: str):
    """
    Serve preview audio file with caching headers.
    
    Args:
        preview_id: Unique preview identifier
        
    Returns:
        Audio file for playback with optimized headers
    """
    # Validate preview_id format
    if not preview_id or len(preview_id) < 10:
        raise HTTPException(400, "Invalid preview ID")
    
    # Find preview file
    preview_path = settings.outputs_dir / "previews" / f"{preview_id}.wav"
    
    if not preview_path.exists():
        raise HTTPException(404, "Preview not found")
    
    # Security check: ensure file is within previews directory
    try:
        preview_path.resolve().relative_to((settings.outputs_dir / "previews").resolve())
    except ValueError:
        raise HTTPException(403, "Access denied")
    
    # Return audio file with optimized headers
    return FileResponse(
        path=str(preview_path),
        media_type="audio/wav",
        headers={
            "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
            "Content-Disposition": "inline",  # Play in browser
            "Accept-Ranges": "bytes",  # Support range requests
            "X-Content-Type-Options": "nosniff"  # Security header
        }
    )

@router.get("/parameters/defaults")
async def get_default_parameters():
    """
    Get default TTS parameters with explanations.
    
    Returns:
        Default parameters with descriptions and ranges
    """
    return {
        "parameters": {
            "length_scale": {
                "default": 1.0,
                "range": [0.5, 2.0],
                "step": 0.1,
                "description": "Vitesse de parole (0.5=rapide, 1.0=normale, 2.0=lente)",
                "explanation": "Contrôle la rapidité d'élocution sans affecter la qualité"
            },
            "noise_scale": {
                "default": 0.667,
                "range": [0.0, 1.0],
                "step": 0.1,
                "description": "Expressivité de la voix (0=monotone, 1=très expressive)",
                "explanation": "Ajoute des variations naturelles pour éviter une voix robotique"
            },
            "noise_w": {
                "default": 0.8,
                "range": [0.0, 1.0],
                "step": 0.1,
                "description": "Stabilité du pitch (0=très stable, 1=très variable)",
                "explanation": "Contrôle les variations de hauteur de voix"
            },
            "sentence_silence": {
                "default": 0.35,
                "range": [0.1, 2.0],
                "step": 0.05,
                "description": "Pause entre phrases en secondes",
                "explanation": "Durée des silences pour une écoute confortable"
            }
        },
        "presets": {
            "audiobook_natural": {
                "length_scale": 0.95,
                "noise_scale": 0.7,
                "noise_w": 0.8,
                "sentence_silence": 0.5,
                "description": "Optimisé pour l'écoute de livres audio"
            },
            "news_fast": {
                "length_scale": 1.1,
                "noise_scale": 0.5,
                "noise_w": 0.6,
                "sentence_silence": 0.25,
                "description": "Lecture rapide et claire pour actualités"
            },
            "storytelling": {
                "length_scale": 0.9,
                "noise_scale": 0.9,
                "noise_w": 0.9,
                "sentence_silence": 0.6,
                "description": "Expressif pour contes et histoires"
            }
        }
    }

@router.get("/voices/install-guide")
async def get_voice_installation_guide():
    """
    Provide guide for installing additional voice models.
    
    Returns:
        Installation instructions and download links
    """
    return {
        "installation_guide": {
            "step_1": {
                "title": "Télécharger les voix depuis GitHub",
                "url": "https://github.com/rhasspy/piper/releases/latest",
                "instructions": [
                    "Aller sur la page des releases Piper",
                    "Télécharger les fichiers voice-*.tar.gz",
                    "Ou utiliser le script : ./scripts/install-voices.sh"
                ]
            },
            "step_2": {
                "title": "Extraire dans le bon répertoire",
                "commands": [
                    "cd backend/voices/",
                    "tar -xzf ~/Downloads/voice-fr-*.tar.gz",
                    "tar -xzf ~/Downloads/voice-en-*.tar.gz"
                ]
            },
            "step_3": {
                "title": "Vérifier l'installation",
                "endpoint": "/api/preview/voices",
                "expected": "Les nouvelles voix apparaissent dans la liste"
            }
        },
        "recommended_voices": {
            "french": [
                {
                    "name": "siwis-medium",
                    "file": "fr_FR-siwis-medium.onnx",
                    "quality": "Meilleur équilibre qualité/vitesse",
                    "download_url": "https://github.com/rhasspy/piper/releases/download/v1.2.0/voice-fr-siwis-medium.tar.gz"
                },
                {
                    "name": "upmc-high", 
                    "file": "fr_FR-upmc-high.onnx",
                    "quality": "Très haute qualité, plus lent",
                    "download_url": "https://github.com/rhasspy/piper/releases/download/v1.2.0/voice-fr-upmc-high.tar.gz"
                }
            ],
            "multilingual": [
                {
                    "name": "amy-english",
                    "file": "en_US-amy-medium.onnx", 
                    "quality": "Anglais américain naturel",
                    "download_url": "https://github.com/rhasspy/piper/releases/download/v1.2.0/voice-en-us-amy-medium.tar.gz"
                }
            ]
        },
        "current_status": {
            "voices_directory": str(settings.voices_dir),
            "writable": settings.voices_dir.exists() and os.access(settings.voices_dir, os.W_OK),
            "disk_space": "Check available disk space for voice downloads (~100MB per voice)"
        }
    }

@router.post("/voices/validate")
async def validate_voice_installation():
    """
    Validate all installed voice models.
    
    Returns:
        Validation results for each voice model
    """
    if not settings.voices_dir.exists():
        raise HTTPException(404, "Voices directory not found")
    
    validation_results = []
    
    for model_file in settings.voices_dir.rglob("*.onnx"):
        result = {
            "model_path": str(model_file),
            "model_exists": model_file.exists(),
            "json_exists": model_file.with_suffix(".onnx.json").exists(),
            "readable": os.access(model_file, os.R_OK) if model_file.exists() else False,
            "file_size_mb": round(model_file.stat().st_size / (1024 * 1024), 2) if model_file.exists() else 0,
            "can_load": False,
            "error": None
        }
        
        # Test if Piper can load the model
        if result["model_exists"] and result["readable"]:
            try:
                # Quick test: piper --model <model> --help should work
                test_cmd = subprocess.run(
                    ["piper", "--model", str(model_file), "--help"],
                    capture_output=True,
                    timeout=10,
                    text=True
                )
                result["can_load"] = test_cmd.returncode == 0
                if test_cmd.returncode != 0:
                    result["error"] = test_cmd.stderr.strip()
            except Exception as e:
                result["error"] = str(e)
        
        validation_results.append(result)
    
    # Summary
    total_models = len(validation_results)
    working_models = len([r for r in validation_results if r["can_load"]])
    
    return {
        "validation_results": validation_results,
        "summary": {
            "total_models": total_models,
            "working_models": working_models,
            "success_rate": round(working_models / total_models * 100, 1) if total_models > 0 else 0,
            "piper_available": shutil.which("piper") is not None
        },
        "recommendations": _generate_validation_recommendations(validation_results)
    }

def _generate_validation_recommendations(results: List[Dict]) -> List[str]:
    """Generate recommendations based on validation results."""
    recommendations = []
    
    working_count = len([r for r in results if r["can_load"]])
    total_count = len(results)
    
    if total_count == 0:
        recommendations.append("Aucun modèle vocal installé. Utilisez ./scripts/install-voices.sh")
    elif working_count == 0:
        recommendations.append("Aucun modèle vocal fonctionnel. Vérifiez l'installation de Piper TTS")
    elif working_count < total_count:
        broken_count = total_count - working_count
        recommendations.append(f"{broken_count} modèle(s) défaillant(s). Vérifiez les erreurs ci-dessus")
    
    # Check for missing JSON files
    missing_json = [r for r in results if r["model_exists"] and not r["json_exists"]]
    if missing_json:
        recommendations.append(f"{len(missing_json)} modèle(s) sans métadonnées JSON. Fonctionnement possible mais sous-optimal")
    
    # Recommend quality upgrades
    low_quality_only = all(r.get("quality") == "low" for r in results if "quality" in r)
    if low_quality_only and working_count > 0:
        recommendations.append("Seuls des modèles 'low quality' détectés. Considérez installer des modèles 'medium' ou 'high'")
    
    return recommendations

@router.delete("/audio/{preview_id}")
async def delete_preview(preview_id: str):
    """Delete preview audio file to save storage."""
    if not preview_id or len(preview_id) < 10:
        raise HTTPException(400, "Invalid preview ID")
    
    preview_path = settings.outputs_dir / "previews" / f"{preview_id}.wav"
    
    if preview_path.exists():
        try:
            preview_path.unlink()
            return {"message": "Preview deleted successfully"}
        except Exception as e:
            raise HTTPException(500, f"Failed to delete preview: {str(e)}")
    else:
        return {"message": "Preview not found (may already be deleted)"}

@router.post("/cleanup")
async def cleanup_old_previews(max_age_hours: int = 24):
    """
    Clean up preview files older than specified hours.
    
    Args:
        max_age_hours: Maximum age in hours before cleanup
        
    Returns:
        Cleanup statistics with storage info
    """
    import time
    
    previews_dir = settings.outputs_dir / "previews"
    if not previews_dir.exists():
        return {"deleted": 0, "message": "No previews directory"}
    
    current_time = time.time()
    deleted_count = 0
    total_size_deleted = 0
    
    for preview_file in previews_dir.glob("*.wav"):
        # Check file age
        file_age_seconds = current_time - preview_file.stat().st_mtime
        file_age_hours = file_age_seconds / 3600
        
        if file_age_hours > max_age_hours:
            try:
                file_size = preview_file.stat().st_size
                preview_file.unlink()
                deleted_count += 1
                total_size_deleted += file_size
            except Exception:
                pass  # Ignore deletion errors
    
    return {
        "deleted": deleted_count,
        "size_freed_mb": round(total_size_deleted / (1024 * 1024), 2),
        "message": f"Cleaned up {deleted_count} preview files older than {max_age_hours}h"
    }

async def get_voice_model_info(model_path: Path) -> VoiceModelInfo:
    """
    Extract detailed information about a voice model with guaranteed fields.
    
    Args:
        model_path: Path to .onnx voice model file
        
    Returns:
        Detailed voice model information with all required fields
    """
    voice_info = VoiceModelInfo(
        model_path=str(model_path.relative_to(settings.voices_dir)) if settings.voices_dir in model_path.parents else str(model_path),
        name=model_path.stem,
        full_path=str(model_path),
        file_size_mb=round(model_path.stat().st_size / (1024 * 1024), 2) if model_path.exists() else None
    )
    
    # Try to load metadata from .json file
    json_file = model_path.with_suffix(".onnx.json")
    if json_file.exists():
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            voice_info.language = metadata.get("language", {})
            voice_info.dataset = metadata.get("dataset", "unknown")
            voice_info.quality = metadata.get("audio", {}).get("quality", "unknown")
            voice_info.sample_rate = metadata.get("audio", {}).get("sample_rate", 22050)
            
        except Exception as e:
            print(f"Warning: Could not parse metadata for {model_path}: {e}")
    
    return voice_info


def _infer_recommended_usage(voice_info) -> List[str]:
    """
    Infer recommended usage based on voice characteristics.
    This ensures no voice ever has empty/null recommended_usage.
    
    Args:
        voice_info: Voice model information
        
    Returns:
        List of recommended usage types (never empty)
    """
    usage_list = []
    
    # Base usage - every voice can do these
    usage_list.extend(["audiobook", "news"])
    
    # Quality-based recommendations
    if hasattr(voice_info, 'quality'):
        if voice_info.quality == "high":
            usage_list.extend(["documentary", "professional"])
        elif voice_info.quality == "low":
            usage_list.append("educational")  # Fast for educational content
    
    # Dataset-based recommendations  
    if hasattr(voice_info, 'dataset'):
        dataset = voice_info.dataset.lower()
        if "siwis" in dataset:
            usage_list.append("storytelling")
        elif "tom" in dataset:
            usage_list.extend(["storytelling", "entertainment"])
        elif "upmc" in dataset:
            usage_list.extend(["educational", "dialogue"])
        elif "bernard" in dataset:
            usage_list.extend(["documentary", "professional"])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_usage = []
    for usage in usage_list:
        if usage not in seen:
            seen.add(usage)
            unique_usage.append(usage)
    
    # Fallback: if somehow still empty, provide defaults
    return unique_usage if unique_usage else ["audiobook", "news"]


