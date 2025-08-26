"""Enhanced text preprocessing for French TTS with proper accent handling."""

import subprocess
import os
import re
import unicodedata
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.exceptions import TTSError


class PreviewTTSEngine:
    """TTS engine with improved French text preprocessing."""
    
    def __init__(
        self,
        voice_model: Optional[str] = None,
        length_scale: Optional[float] = None,
        noise_scale: Optional[float] = None,
        noise_w: Optional[float] = None,
        sentence_silence: Optional[float] = None,
    ):
        """Initialize Preview TTS engine."""
        self.voice_model = voice_model or settings.voice_model
        self.length_scale = length_scale or settings.length_scale
        self.noise_scale = noise_scale or settings.noise_scale
        self.noise_w = noise_w or settings.noise_w
        self.sentence_silence = sentence_silence or settings.sentence_silence
        
        # Validate parameters
        self._validate_parameters()
        
        # Resolve voice model path
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
        """Resolve and validate voice model path."""
        search_strategies = [
            Path(self.voice_model),
            Path("backend") / self.voice_model,
            Path.cwd() / self.voice_model,
            Path.cwd() / "backend" / self.voice_model,
            settings.voices_dir / self.voice_model,
        ]
        
        for strategy_path in search_strategies:
            abs_path = strategy_path.resolve()
            if abs_path.exists() and abs_path.is_file():
                return abs_path
        
        # Fallback: find any available .onnx file
        fallback_model = self._find_fallback_voice_model()
        if fallback_model:
            return fallback_model
        
        raise TTSError(f"Voice model not found: {self.voice_model}")
    
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
                    return onnx_files[0]
        
        return None
    
    def text_to_wav(self, text: str, output_path: Path) -> None:
        """Convert text to WAV with improved French preprocessing."""
        if len(text) > 500:
            raise TTSError("Preview text too long (max 500 characters)")
        
        if not text.strip():
            raise TTSError("Empty text provided for preview")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            cmd = [
                "piper",
                "--model", str(self.voice_model_path),
                "--output_file", str(output_path),
                "--length_scale", str(self.length_scale),
                "--noise_scale", str(self.noise_scale),
                "--noise_w", str(self.noise_w),
                "--sentence_silence", str(self.sentence_silence),
            ]
            
            # IMPROVED: French-optimized text cleaning
            clean_text = self._clean_french_text(text)
            text_input = clean_text.strip() + "\n"
            
            print(f"🎤 Original text: {text[:100]}...")
            print(f"🧹 Cleaned text: {clean_text[:100]}...")
            print(f"📊 Character preservation: {len(clean_text)}/{len(text)} chars")
            
            result = subprocess.run(
                cmd,
                input=text_input,
                text=True,
                check=True,
                capture_output=True,
                timeout=30,
                # IMPORTANT: Specify UTF-8 encoding explicitly
                encoding='utf-8'
            )
            
            if result.stdout:
                print(f"✅ Piper output: {result.stdout.strip()}")
            if result.stderr:
                print(f"⚠️  Piper warnings: {result.stderr.strip()}")
            
            if not output_path.exists():
                raise TTSError("No audio file generated")
            
            file_size = output_path.stat().st_size
            if file_size == 0:
                raise TTSError("Generated audio file is empty")
            
            print(f"🎵 Preview generated: {output_path.name} ({file_size:,} bytes)")
                
        except subprocess.TimeoutExpired:
            raise TTSError("Preview generation timed out (>30s)")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else "Unknown Piper error"
            raise TTSError(f"Piper TTS failed: {error_msg}")
        except FileNotFoundError:
            raise TTSError("Piper TTS binary not found in PATH")
        except Exception as e:
            raise TTSError(f"Unexpected error: {str(e)}")
    
    def _clean_french_text(self, text: str) -> str:
        """
        Clean text for French TTS while preserving accents and special characters.
        
        CRITICAL: This function now preserves French accents properly.
        """
        # STEP 1: Normalize to NFC (composed form) - BETTER for French TTS
        # NFC keeps accented characters as single units (é, à, ç)
        # This is opposite of the previous NFKD which decomposed them
        text = unicodedata.normalize("NFC", text)
        
        # STEP 2: Remove only truly problematic characters, preserve French accents
        # Keep: a-z, A-Z, 0-9, French accented chars, basic punctuation, spaces
        french_chars_pattern = r'[a-zA-Z0-9àáâäçèéêëïîôùûüÿñæœÀÁÂÄÇÈÉÊËÏÎÔÙÛÜŸÑÆŒ\s\.,!?;:()\-\'"«»…–—]'
        
        # Remove characters that are NOT in our allowed set
        text = ''.join(c for c in text if re.match(french_chars_pattern, c))
        
        # STEP 3: Clean whitespace only (preserve word structure)
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces -> single space
        text = re.sub(r'\n{3,}', '\n\n', text)  # Excessive newlines -> double
        
        # STEP 4: Fix punctuation spacing (French typography rules)
        text = re.sub(r'\s+([.!?])', r'\1', text)  # Remove space before sentence ending
        text = re.sub(r'([.!?])\s*([A-ZÀÁÂÄÈÉÊËÌÍÎÏÒÓÔÖÙÚÛÜŸ])', r'\1 \2', text)  # Space after sentence
        
        # STEP 5: Ensure proper sentence ending
        text = text.strip()
        if text and text[-1] not in '.!?':
            text += '.'
        
        return text
    
    @staticmethod
    def test_text_preprocessing():
        """Test function to verify French text preprocessing."""
        test_cases = [
            "Bonjour ! Ceci est un aperçu de la voix française pour la conversion de vos livres audio. Vous pouvez ajuster la vitesse, l'expressivité et d'autres paramètres selon vos préférences.",
            "À côté de chez moi, il y a un café très célèbre où l'on sert des crêpes délicieuses.",
            "L'hôtel était magnifique, avec une piscine, un jardin fleuri et une vue imprenable sur la mer Méditerranée.",
            "Les élèves étudient français, mathématiques, histoire-géographie et éducation physique."
        ]
        
        engine = PreviewTTSEngine()
        
        print("🧪 Testing French text preprocessing:")
        for i, test_text in enumerate(test_cases, 1):
            cleaned = engine._clean_french_text(test_text)
            print(f"\nTest {i}:")
            print(f"  Original:  {test_text}")
            print(f"  Cleaned:   {cleaned}")
            print(f"  Preserved: {len(cleaned)}/{len(test_text)} characters")
            
            # Count French accented characters
            accents = sum(1 for c in cleaned if c in 'àáâäçèéêëïîôùûüÿñæœÀÁÂÄÇÈÉÊËÏÎÔÙÛÜŸÑÆŒ')
            print(f"  Accents:   {accents} preserved")


# Additional utility functions for text analysis
def analyze_text_encoding(text: str) -> dict:
    """Analyze text encoding and character composition."""
    analysis = {
        "length": len(text),
        "encoding": "utf-8",
        "normalization": {
            "NFC": len(unicodedata.normalize("NFC", text)),
            "NFD": len(unicodedata.normalize("NFD", text)),
            "NFKC": len(unicodedata.normalize("NFKC", text)),
            "NFKD": len(unicodedata.normalize("NFKD", text))
        },
        "character_categories": {},
        "french_accents": sum(1 for c in text if c in 'àáâäçèéêëïîôùûüÿñæœÀÁÂÄÇÈÉÊËÏÎÔÙÛÜŸÑÆŒ'),
        "ascii_only": text.isascii()
    }
    
    # Count Unicode categories
    for char in text:
        category = unicodedata.category(char)
        analysis["character_categories"][category] = analysis["character_categories"].get(category, 0) + 1
    
    return analysis


def compare_preprocessing_methods(text: str) -> dict:
    """Compare different text preprocessing approaches."""
    methods = {
        "original": text,
        "nfc_normalized": unicodedata.normalize("NFC", text),
        "nfd_normalized": unicodedata.normalize("NFD", text),
        "nfkd_normalized": unicodedata.normalize("NFKD", text),
        "ascii_only": text.encode('ascii', errors='ignore').decode('ascii'),
        "french_optimized": PreviewTTSEngine()._clean_french_text(text)
    }
    
    comparison = {}
    for method, result in methods.items():
        comparison[method] = {
            "text": result,
            "length": len(result),
            "accents_count": sum(1 for c in result if c in 'àáâäçèéêëïîôùûüÿñæœÀÁÂÄÇÈÉÊËÏÎÔÙÛÜŸÑÆŒ'),
            "ascii_only": result.isascii()
        }
    
    return comparison


if __name__ == "__main__":
    # Run tests
    PreviewTTSEngine.test_text_preprocessing()
    
    # Analyze specific problematic text
    problematic_text = "Bonjour ! Ceci est un aperçu de la voix française pour la conversion de vos livres audio. Vous pouvez ajuster la vitesse, l'expressivité et d'autres paramètres selon vos préférences."
    
    print("\n" + "="*80)
    print("📊 DETAILED ANALYSIS OF PROBLEMATIC TEXT")
    print("="*80)
    
    analysis = analyze_text_encoding(problematic_text)
    print(f"Text analysis: {analysis}")
    
    print("\n🔍 PREPROCESSING METHOD COMPARISON:")
    comparison = compare_preprocessing_methods(problematic_text)
    for method, data in comparison.items():
        print(f"\n{method.upper()}:")
        print(f"  Text: {data['text']}")
        print(f"  Length: {data['length']} | Accents: {data['accents_count']} | ASCII only: {data['ascii_only']}")