"""Application startup checks and validations."""

import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

from app.core.config import settings
from app.core.exceptions import TTSError


class StartupValidator:
    """Validates application dependencies and configuration at startup."""
    
    @staticmethod
    def validate_all() -> Dict[str, bool]:
        """
        Run all startup validations.
        
        Returns:
            Dictionary with validation results
        """
        results = {}
        
        try:
            results["piper_tts"] = StartupValidator.validate_piper_tts()
        except Exception as e:
            print(f"⚠️  Piper TTS validation failed: {e}")
            results["piper_tts"] = False
        
        try:
            results["voice_models"] = StartupValidator.validate_voice_models()
        except Exception as e:
            print(f"⚠️  Voice models validation failed: {e}")
            results["voice_models"] = False
        
        try:
            results["directories"] = StartupValidator.validate_directories()
        except Exception as e:
            print(f"⚠️  Directories validation failed: {e}")
            results["directories"] = False
        
        try:
            results["dependencies"] = StartupValidator.validate_python_dependencies()
        except Exception as e:
            print(f"⚠️  Dependencies validation failed: {e}")
            results["dependencies"] = False
        
        return results
    
    @staticmethod
    def validate_piper_tts() -> bool:
        """
        Validate Piper TTS installation.
        
        Returns:
            True if Piper TTS is available and working
            
        Raises:
            TTSError: If Piper TTS validation fails
        """
        # Check if piper binary exists in PATH
        piper_path = shutil.which("piper")
        if not piper_path:
            raise TTSError(
                "Piper TTS binary not found in PATH. "
                "Please install Piper TTS or run './scripts/install-piper.sh'"
            )
        
        print(f"✅ Piper TTS found at: {piper_path}")
        
        # Test piper execution
        try:
            result = subprocess.run(
                ["piper", "--help"],
                capture_output=True,
                text=True,
                timeout=10,
                check=True
            )
            
            # Check if help output contains expected content
            if "text-to-speech" not in result.stdout.lower() and "piper" not in result.stdout.lower():
                raise TTSError("Piper binary found but does not appear to be Piper TTS")
            
            print("✅ Piper TTS is responding correctly")
            return True
            
        except subprocess.TimeoutExpired:
            raise TTSError("Piper TTS binary is not responding (timeout)")
        except subprocess.CalledProcessError as e:
            raise TTSError(f"Piper TTS execution failed: {e.stderr}")
        except Exception as e:
            raise TTSError(f"Piper TTS validation error: {str(e)}")
    
    @staticmethod
    def validate_voice_models() -> bool:
        """
        Validate voice model availability.
        
        Returns:
            True if voice models are found and valid
        """
        voice_model_path = Path(settings.voice_model)
        
        # Check if default voice model exists
        if not voice_model_path.exists():
            available_models = StartupValidator._find_voice_models()
            if available_models:
                print(f"⚠️  Default voice model not found: {settings.voice_model}")
                print("Available models:")
                for model in available_models[:3]:  # Show first 3
                    print(f"   - {model}")
                return False
            else:
                raise TTSError(
                    f"No voice models found. Please download voice models to {settings.voices_dir}. "
                    "See: https://github.com/rhasspy/piper/releases"
                )
        
        print(f"✅ Default voice model found: {voice_model_path}")
        
        # Validate model file format
        if not voice_model_path.suffix.lower() == ".onnx":
            raise TTSError(f"Voice model must be .onnx format, got: {voice_model_path.suffix}")
        
        # Check for companion .json file
        json_file = voice_model_path.with_suffix(".onnx.json")
        if not json_file.exists():
            print(f"⚠️  Voice model metadata not found: {json_file}")
            print("   Model may work but metadata is recommended")
        else:
            print(f"✅ Voice model metadata found: {json_file}")
        
        return True
    
    @staticmethod
    def _find_voice_models() -> List[str]:
        """Find all available voice models in the voices directory."""
        if not settings.voices_dir.exists():
            return []
        
        models = []
        for model_file in settings.voices_dir.rglob("*.onnx"):
            models.append(str(model_file.relative_to(settings.voices_dir)))
        
        return sorted(models)
    
    @staticmethod
    def validate_directories() -> bool:
        """
        Validate and create required directories.
        
        Returns:
            True if all directories are ready
        """
        directories = [
            settings.voices_dir,
            settings.storage_dir,
            settings.uploads_dir,
            settings.outputs_dir,
            settings.outputs_dir / "previews"  # For voice previews
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                
                # Test write permissions
                test_file = directory / ".write_test"
                test_file.touch()
                test_file.unlink()
                
                print(f"✅ Directory ready: {directory}")
                
            except Exception as e:
                raise TTSError(f"Cannot create/access directory {directory}: {str(e)}")
        
        return True
    
    @staticmethod
    def validate_python_dependencies() -> bool:
        """
        Validate critical Python dependencies.
        
        Returns:
            True if all dependencies are available
        """
        critical_deps = [
            ("fastapi", "FastAPI web framework"),
            ("uvicorn", "ASGI server"), 
            ("PyPDF2", "PDF text extraction"),
            ("ebooklib", "EPUB text extraction"),
            ("bs4", "HTML parsing (BeautifulSoup)"),
            ("pydantic", "Data validation"),
        ]
        
        missing_deps = []
        
        for module_name, description in critical_deps:
            try:
                __import__(module_name)
                print(f"✅ {description}: {module_name}")
            except ImportError:
                missing_deps.append((module_name, description))
        
        if missing_deps:
            print("❌ Missing dependencies:")
            for module_name, description in missing_deps:
                print(f"   - {module_name}: {description}")
            raise TTSError(
                "Missing critical dependencies. "
                "Please run: pip install -r requirements.txt"
            )
        
        return True
    
    @staticmethod
    def get_system_info() -> Dict[str, str]:
        """Get system information for debugging."""
        import sys
        import platform
        
        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
            "piper_path": shutil.which("piper") or "Not found",
            "voice_model": str(settings.voice_model),
            "voices_dir": str(settings.voices_dir),
            "storage_dir": str(settings.storage_dir)
        }
    
    @staticmethod
    def print_startup_summary(results: Dict[str, bool]) -> None:
        """Print startup validation summary."""
        print("\n" + "="*60)
        print("🚀 AUDIO BOOK CONVERTER - STARTUP VALIDATION")
        print("="*60)
        
        total_checks = len(results)
        passed_checks = sum(results.values())
        
        for check_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            check_display = check_name.replace("_", " ").title()
            print(f"{status} {check_display}")
        
        print("-" * 60)
        print(f"Validation Results: {passed_checks}/{total_checks} checks passed")
        
        if passed_checks == total_checks:
            print("🎉 All validations passed! Application ready to start.")
        else:
            print("⚠️  Some validations failed. Check errors above.")
            if not results.get("piper_tts", True):
                print("\n💡 To install Piper TTS:")
                print("   ./scripts/install-piper.sh")
                print("   # or manually from: https://github.com/rhasspy/piper/releases")
            
            if not results.get("voice_models", True):
                print("\n💡 To download voice models:")
                print("   mkdir -p backend/voices")
                print("   # Download from: https://github.com/rhasspy/piper/releases")
        
        print("="*60 + "\n")


def run_startup_checks() -> bool:
    """
    Run all startup checks and return success status.
    
    Returns:
        True if all checks pass, False otherwise
    """
    try:
        validator = StartupValidator()
        results = validator.validate_all()
        validator.print_startup_summary(results)
        
        # Return True only if all checks pass
        return all(results.values())
        
    except Exception as e:
        print(f"💥 Startup validation crashed: {e}")
        return False