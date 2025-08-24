"""Enhanced lightweight TTS service for voice previews with all Piper parameters."""

import subprocess
import os
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.exceptions import TTSError


class PreviewTTSEngine:
    """
    Enhanced TTS engine for generating voice previews with full parameter control.
    Supports all Piper TTS parameters for comprehensive voice testing.
    """
    
    def __init__(
        self,
        voice_model: Optional[str] = None,
        length_scale: Optional[float] = None,
        noise_scale: Optional[float] = None,
        noise_w: Optional[float] = None,
        sentence_silence: Optional[float] = None,
    ):
        """
        Initialize Preview TTS engine with full parameter support.
        
        Args:
            voice_model: Path to voice model (.onnx file)
            length_scale: Speech speed (0.5-2.0, default 1.0)
            noise_scale: Voice expressivity/variation (0.0-1.0, default 0.667)
            noise_w: Pitch stability control (0.0-1.0, default 0.8)
            sentence_silence: Pause between sentences in seconds (0.1-2.0, default 0.35)
        """
        self.voice_model = voice_model or settings.voice_model
        self.length_scale = length_scale or settings.length_scale
        self.noise_scale = noise_scale or settings.noise_scale
        self.noise_w = noise_w or settings.noise_w
        self.sentence_silence = sentence_silence or settings.sentence_silence
        
        # Validate parameters
        self._validate_parameters()
        
        # Resolve and validate voice model path
        self.voice_model_path = self._resolve_voice_model_path()
    
    def _validate_parameters(self) -> None:
        """Validate TTS parameters are within acceptable ranges."""
        validations = [
            (self.length_scale, 0.5, 2.0, "length_scale"),
            (self.noise_scale, 0.0, 1.0, "noise_scale"), 
            (self.noise_w, 0.0, 1.0, "noise_w"),
            (self.sentence_silence, 0.1, 2.0, "sentence_silence")
        ]
        
        for value, min_val, max_val, param_name in validations:
            if not (min_val <= value <= max_val):
                raise TTSError(f"Parameter {param_name}={value} out of range [{min_val}, {max_val}]")
    
    def _resolve_voice_model_path(self) -> Path:
        """
        Resolve and validate voice model path with comprehensive search.
        
        Returns:
            Absolute path to voice model
            
        Raises:
            TTSError: If voice model not found with detailed diagnostics
        """
        # Try multiple path resolution strategies
        search_strategies = [
            Path(self.voice_model),  # Direct path as given
            Path("backend") / self.voice_model,  # With backend/ prefix
            Path.cwd() / self.voice_model,  # From current working directory
            Path.cwd() / "backend" / self.voice_model,  # From project root
            settings.voices_dir / self.voice_model,  # From voices directory
        ]
        
        print(f"🔍 Searching for voice model: {self.voice_model}")
        print(f"📁 Current working directory: {Path.cwd()}")
        print(f"🎤 Voices directory setting: {settings.voices_dir}")
        
        for strategy_path in search_strategies:
            abs_path = strategy_path.resolve()
            if abs_path.exists() and abs_path.is_file():
                print(f"✅ Found voice model: {abs_path}")
                return abs_path
            else:
                print(f"  ❌ Not found: {abs_path}")
        
        # Fallback: find any available .onnx file
        fallback_model = self._find_fallback_voice_model()
        if fallback_model:
            print(f"⚡ Using fallback model: {fallback_model}")
            return fallback_model
        
        # Generate comprehensive error with diagnostics
        error_details = self._generate_voice_error_diagnostics()
        raise TTSError(f"Voice model not found: {self.voice_model}\n{error_details}")
    
    def _find_fallback_voice_model(self) -> Optional[Path]:
        """Find any available voice model as fallback."""
        search_dirs = [
            Path("voices"),
            Path("backend/voices"),
            Path.cwd() / "voices",
            Path.cwd() / "backend/voices",
            settings.voices_dir
        ]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                onnx_files = list(search_dir.rglob("*.onnx"))
                if onnx_files:
                    print(f"📂 Found {len(onnx_files)} voice models in {search_dir}")
                    # Prefer models with metadata
                    for onnx_file in onnx_files:
                        if onnx_file.with_suffix(".onnx.json").exists():
                            return onnx_file
                    # Fallback to any model
                    return onnx_files[0]
        
        return None
    
    def _generate_voice_error_diagnostics(self) -> str:
        """Generate detailed diagnostics for voice model errors."""
        diagnostics = []
        
        # Current directory info
        diagnostics.append(f"Working directory: {Path.cwd()}")
        diagnostics.append(f"Voices directory: {settings.voices_dir} (exists: {settings.voices_dir.exists()})")
        
        # List available voice models
        available_models = []
        for search_dir in [Path("voices"), Path("backend/voices"), settings.voices_dir]:
            if search_dir.exists():
                models = list(search_dir.rglob("*.onnx"))
                available_models.extend(models)
        
        if available_models:
            diagnostics.append(f"Available models ({len(available_models)}):")
            for model in available_models[:5]:  # Show first 5
                diagnostics.append(f"  - {model}")
            if len(available_models) > 5:
                diagnostics.append(f"  ... and {len(available_models) - 5} more")
        else:
            diagnostics.append("No .onnx voice models found in any directory")
        
        # Installation suggestions
        diagnostics.append("\n💡 Solutions:")
        diagnostics.append("  1. Download voices: ./scripts/install-voices.sh")
        diagnostics.append("  2. Manual download: https://github.com/rhasspy/piper/releases")
        diagnostics.append("  3. Check voice model path in .env file")
        
        return "\n".join(diagnostics)
    
    def text_to_wav(self, text: str, output_path: Path) -> None:
        """
        Convert text to WAV audio with full parameter control.
        
        Args:
            text: Text content to synthesize (max 500 chars for preview)
            output_path: Path where WAV file will be saved
            
        Raises:
            TTSError: If synthesis fails with detailed error info
        """
        # Validate input
        if len(text) > 500:
            raise TTSError("Preview text too long (max 500 characters)")
        
        if not text.strip():
            raise TTSError("Empty text provided for preview")
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Build comprehensive Piper command with all parameters
            cmd = [
                "piper",
                "--model", str(self.voice_model_path),
                "--output_file", str(output_path),
                "--length_scale", str(self.length_scale),
                "--noise_scale", str(self.noise_scale),
                "--noise_w", str(self.noise_w),
                "--sentence_silence", str(self.sentence_silence),
            ]
            
            # Clean and prepare text
            clean_text = self._clean_preview_text(text)
            text_input = clean_text.strip() + "\n"
            
            print(f"🎤 Generating preview with enhanced parameters:")
            print(f"   Model: {self.voice_model_path}")
            print(f"   Speed: {self.length_scale}x")
            print(f"   Expressivity: {self.noise_scale}")
            print(f"   Pitch stability: {self.noise_w}")
            print(f"   Sentence pause: {self.sentence_silence}s")
            print(f"   Text: {clean_text[:50]}{'...' if len(clean_text) > 50 else ''}")
            
            # Execute Piper TTS with enhanced error handling
            result = subprocess.run(
                cmd,
                input=text_input,
                text=True,
                check=True,
                capture_output=True,
                timeout=30  # 30 second timeout for previews
            )
            
            if result.stdout:
                print(f"✅ Piper output: {result.stdout.strip()}")
            if result.stderr:
                print(f"⚠️  Piper warnings: {result.stderr.strip()}")
            
            # Verify output file quality
            if not output_path.exists():
                raise TTSError("No audio file generated")
            
            file_size = output_path.stat().st_size
            if file_size == 0:
                raise TTSError("Generated audio file is empty")
            elif file_size < 1000:  # Less than 1KB seems suspicious
                print(f"⚠️  Generated audio file is very small: {file_size} bytes")
            
            print(f"🎵 Preview generated successfully: {output_path.name} ({file_size:,} bytes)")
                
        except subprocess.TimeoutExpired:
            raise TTSError(
                f"Preview generation timed out (>30s). "
                f"Try with shorter text or different parameters."
            )
        except subprocess.CalledProcessError as e:
            # Enhanced error parsing
            error_msg = e.stderr.strip() if e.stderr else "Unknown Piper error"
            
            # Common error patterns and user-friendly messages
            if "model not found" in error_msg.lower():
                error_msg = f"Modèle vocal non trouvé: {self.voice_model_path}"
            elif "invalid model" in error_msg.lower():
                error_msg = f"Modèle vocal corrompu ou incompatible"
            elif "out of memory" in error_msg.lower():
                error_msg = "Mémoire insuffisante. Essayez avec un texte plus court"
            elif "permission denied" in error_msg.lower():
                error_msg = f"Permissions insuffisantes pour accéder au modèle vocal"
            
            raise TTSError(f"Piper TTS failed: {error_msg}")
        except FileNotFoundError:
            raise TTSError(
                "Piper TTS binary not found in PATH. "
                "Install with: ./scripts/install-piper.sh"
            )
        except Exception as e:
            raise TTSError(f"Unexpected error during TTS generation: {str(e)}")
    
    def _clean_preview_text(self, text: str) -> str:
        """
        Clean and normalize text for optimal TTS generation.
        
        Args:
            text: Raw text input
            
        Returns:
            Cleaned text optimized for TTS
        """
        import re
        import unicodedata
        
        # Unicode normalization (decompose then remove combining chars)
        text = unicodedata.normalize("NFKD", text)
        text = "".join(c for c in text if not unicodedata.combining(c))
        
        # Remove excessive whitespace while preserving structure
        text = re.sub(r"[ \t]+", " ", text)  # Multiple spaces -> single space
        text = re.sub(r"\n{3,}", "\n\n", text)  # Too many newlines -> double
        
        # Remove problematic characters but keep punctuation
        text = re.sub(r"[^\w\s\.,!?;:()\-'\"'«»…–—]", " ", text, flags=re.UNICODE)
        
        # Fix spacing around punctuation
        text = re.sub(r"\s+([.!?])", r"\1", text)  # Remove spaces before sentence endings
        text = re.sub(r"([.!?])\s*([A-ZÀÁÂÄÈÉÊËÌÍÎÏÒÓÔÖÙÚÛÜ])", r"\1 \2", text)  # Ensure space after
        
        # Ensure proper sentence ending for natural pause
        text = text.strip()
        if text and text[-1] not in ".!?":
            text += "."
        
        return text
    
    def get_model_info(self) -> dict:
        """
        Get information about the current voice model.
        
        Returns:
            Dictionary with model metadata and parameters
        """
        info = {
            "model_path": str(self.voice_model_path),
            "model_name": self.voice_model_path.stem,
            "model_exists": self.voice_model_path.exists(),
            "model_size_mb": None,
            "metadata": None,
            "current_parameters": {
                "length_scale": self.length_scale,
                "noise_scale": self.noise_scale,
                "noise_w": self.noise_w,
                "sentence_silence": self.sentence_silence
            }
        }
        
        if self.voice_model_path.exists():
            # Get file size
            info["model_size_mb"] = round(self.voice_model_path.stat().st_size / (1024 * 1024), 2)
            
            # Try to load metadata from companion .json file
            json_file = self.voice_model_path.with_suffix(".onnx.json")
            if json_file.exists():
                try:
                    import json
                    with open(json_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    info["metadata"] = metadata
                except Exception as e:
                    print(f"Warning: Could not parse voice metadata: {e}")
        
        return info
    
    @staticmethod
    def is_available() -> bool:
        """
        Check if Piper TTS is available with version info.
        
        Returns:
            True if Piper TTS is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["piper", "--version"],
                capture_output=True,
                check=True,
                timeout=5,
                text=True
            )
            print(f"✅ Piper TTS version: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError:
            # Try fallback with --help
            try:
                subprocess.run(
                    ["piper", "--help"],
                    capture_output=True,
                    check=True,
                    timeout=5
                )
                print("✅ Piper TTS available (version unknown)")
                return True
            except:
                return False
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    @staticmethod
    def find_voice_models() -> list[Path]:
        """
        Find all available voice models with quality ranking.
        
        Returns:
            List of paths to .onnx voice model files, sorted by quality
        """
        voice_models = []
        search_dirs = [
            Path("voices"),
            Path("backend/voices"),
            Path.cwd() / "voices", 
            Path.cwd() / "backend/voices",
            settings.voices_dir
        ]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                models = list(search_dir.rglob("*.onnx"))
                voice_models.extend(models)
        
        # Remove duplicates and sort by quality preference
        unique_models = list(set(voice_models))
        
        # Sort: high quality first, then medium, then low
        def quality_score(model_path: Path) -> int:
            path_str = str(model_path).lower()
            if "high" in path_str:
                return 3
            elif "medium" in path_str:
                return 2
            elif "low" in path_str:
                return 1
            else:
                return 0  # Unknown quality
        
        return sorted(unique_models, key=quality_score, reverse=True)
    
    @staticmethod
    def get_parameter_explanations() -> dict:
        """
        Get detailed explanations of all TTS parameters.
        
        Returns:
            Dictionary with parameter explanations and examples
        """
        return {
            "length_scale": {
                "name": "Vitesse de parole",
                "description": "Contrôle la rapidité d'élocution sans déformer la voix",
                "technical": "Scaling factor for phoneme durations",
                "range": "0.5 (très rapide) à 2.0 (très lent)",
                "default": 1.0,
                "examples": {
                    0.8: "Lecture rapide (podcasts, actualités)",
                    1.0: "Vitesse naturelle (livres audio)",
                    1.2: "Lecture posée (apprentissage, textes complexes)"
                },
                "impact": "Aucun impact sur la qualité vocale"
            },
            "noise_scale": {
                "name": "Expressivité / Variation de voix",
                "description": "Contrôle les variations naturelles qui rendent la voix vivante",
                "technical": "Random noise injection for voice variation",
                "range": "0.0 (monotone) à 1.0 (très expressive)",
                "default": 0.667,
                "examples": {
                    0.0: "Voix robotique, monotone (lectures techniques)",
                    0.5: "Légèrement expressive (actualités)",
                    0.667: "Naturellement expressive (livres audio)",
                    0.9: "Très expressive (contes pour enfants)"
                },
                "impact": "Valeurs trop élevées peuvent créer des artéfacts"
            },
            "noise_w": {
                "name": "Stabilité du pitch",
                "description": "Contrôle les variations de hauteur de voix",
                "technical": "Noise weighting for pitch stability control",
                "range": "0.0 (pitch très stable) à 1.0 (pitch très variable)",
                "default": 0.8,
                "examples": {
                    0.3: "Voix très stable (voix off institutionnelle)",
                    0.6: "Légèrement variable (podcasts)",
                    0.8: "Naturellement variable (conversation)",
                    1.0: "Très variable (narration dramatique)"
                },
                "impact": "Travaille en synergie avec noise_scale"
            },
            "sentence_silence": {
                "name": "Pause entre phrases",
                "description": "Durée des silences pour une écoute confortable",
                "technical": "Silence duration inserted between sentences",
                "range": "0.1s (lecture rapide) à 2.0s (très posée)",
                "default": 0.35,
                "examples": {
                    0.1: "Lecture très rapide (résumés)",
                    0.25: "Lecture normale (articles)",
                    0.35: "Lecture confortable (livres)",
                    0.6: "Lecture posée (apprentissage)",
                    1.0: "Lecture méditative (poésie)"
                },
                "impact": "N'affecte que les pauses, pas la vitesse de parole"
            }
        }
    
    @staticmethod  
    def get_preset_configurations() -> dict:
        """
        Get predefined parameter presets for common use cases.
        
        Returns:
            Dictionary with preset configurations
        """
        return {
            "audiobook_comfort": {
                "name": "Livre audio confortable",
                "description": "Paramètres optimisés pour une écoute longue et agréable",
                "parameters": {
                    "length_scale": 0.95,  # Slightly faster
                    "noise_scale": 0.7,    # Natural expressivity
                    "noise_w": 0.8,       # Balanced pitch variation
                    "sentence_silence": 0.5  # Comfortable pauses
                },
                "best_for": ["Romans", "Biographies", "Essais"]
            },
            "news_efficient": {
                "name": "Actualités efficace",
                "description": "Lecture rapide et claire pour l'information",
                "parameters": {
                    "length_scale": 1.1,   # Slightly slower for clarity
                    "noise_scale": 0.5,    # Less variation for clarity
                    "noise_w": 0.6,       # Stable pitch
                    "sentence_silence": 0.25  # Quick pauses
                },
                "best_for": ["Articles", "Rapports", "Documentation"]
            },
            "storytelling_dramatic": {
                "name": "Narration dramatique",
                "description": "Expressif et captivant pour les histoires",
                "parameters": {
                    "length_scale": 0.9,   # Faster pace
                    "noise_scale": 0.9,    # Very expressive
                    "noise_w": 0.9,       # Variable pitch
                    "sentence_silence": 0.4  # Dramatic pauses
                },
                "best_for": ["Romans", "Contes", "Théâtre"]
            },
            "learning_careful": {
                "name": "Apprentissage posé",
                "description": "Lecture lente et claire pour l'apprentissage",
                "parameters": {
                    "length_scale": 1.2,   # Slower for comprehension
                    "noise_scale": 0.6,    # Moderate expression
                    "noise_w": 0.7,       # Stable but not monotone
                    "sentence_silence": 0.8  # Long pauses for reflection
                },
                "best_for": ["Manuels", "Cours", "Textes techniques"]
            },
            "meditation_calm": {
                "name": "Méditation calme",
                "description": "Voix apaisante pour la relaxation",
                "parameters": {
                    "length_scale": 1.3,   # Very slow
                    "noise_scale": 0.4,    # Minimal variation
                    "noise_w": 0.5,       # Very stable pitch
                    "sentence_silence": 1.2  # Long meditative pauses
                },
                "best_for": ["Méditations", "Relaxation", "Poésie"]
            }
        }
    
    def apply_preset(self, preset_name: str) -> None:
        """
        Apply a predefined parameter preset.
        
        Args:
            preset_name: Name of the preset to apply
            
        Raises:
            TTSError: If preset not found
        """
        presets = self.get_preset_configurations()
        
        if preset_name not in presets:
            available = ", ".join(presets.keys())
            raise TTSError(f"Preset '{preset_name}' not found. Available: {available}")
        
        preset = presets[preset_name]
        params = preset["parameters"]
        
        self.length_scale = params["length_scale"]
        self.noise_scale = params["noise_scale"] 
        self.noise_w = params["noise_w"]
        self.sentence_silence = params["sentence_silence"]
        
        # Re-validate after applying preset
        self._validate_parameters()
        
        print(f"✅ Applied preset '{preset_name}': {preset['description']}")
        print(f"   Parameters: {params}")
    
    def estimate_generation_time(self, text_length: int) -> float:
        """
        Estimate time needed to generate audio for given text length.
        
        Args:
            text_length: Number of characters in text
            
        Returns:
            Estimated generation time in seconds
        """
        # Base generation time (empirical: ~2-5 chars per second depending on model quality)
        chars_per_second = 3.0  # Conservative estimate
        
        # Adjust for model quality (if known)
        model_info = self.get_model_info()
        if model_info.get("metadata"):
            quality = model_info["metadata"].get("audio", {}).get("quality", "medium")
            if quality == "low":
                chars_per_second = 5.0  # Faster
            elif quality == "high":
                chars_per_second = 2.0  # Slower but better quality
        
        base_time = text_length / chars_per_second
        
        # Add overhead for TTS startup and file writing
        overhead = 2.0  # seconds
        
        return base_time + overhead