"""Application startup checks and validations."""

import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

from app.config import settings
from app.core.exceptions import TTSError


class StartupValidator:
    """Validates application dependencies and configuration at startup."""
    
    @staticmethod
    def validate_all() -> Dict[str, bool]:
        """Run all startup validations."""
        results = {}
        
        # Check Piper binary or Python package
        try:
            results["piper_tts"] = StartupValidator.validate_piper()
        except Exception as e:
            print(f"⚠️  Piper TTS validation: {e}")
            results["piper_tts"] = False
        
        # Check voice models
        try:
            results["voice_models"] = StartupValidator.validate_voice_models()
        except Exception as e:
            print(f"⚠️  Voice models validation: {e}")
            results["voice_models"] = False
        
        # Check directories
        try:
            results["directories"] = StartupValidator.validate_directories()
        except Exception as e:
            print(f"⚠️  Directories validation: {e}")
            results["directories"] = False
        
        # Check Python dependencies
        try:
            results["dependencies"] = StartupValidator.validate_python_dependencies()
        except Exception as e:
            print(f"⚠️  Dependencies validation: {e}")
            results["dependencies"] = False
        
        return results
    
    @staticmethod
    def validate_piper() -> bool:
        """Validate Piper TTS availability (binary or Python package)."""
        # First check for binary
        piper_path = shutil.which("piper")
        if piper_path:
            print(f"✅ Piper binary found at: {piper_path}")
            return True
        
        # Then check for Python package
        try:
            import piper
            print("✅ Piper TTS Python package available")
            return True
        except ImportError:
            print("⚠️  Piper TTS not found (install binary or pip install piper-tts)")
            return False
    
    @staticmethod
    def validate_voice_models() -> bool:
        """Validate voice models availability."""
        voices_dir = Path(settings.voices_dir)
        if not voices_dir.exists():
            voices_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created voices directory: {voices_dir}")
        
        onnx_files = list(voices_dir.glob("**/*.onnx"))
        if not onnx_files:
            print("⚠️  No voice models found - download models to backend/voices/")
            return False
        
        print(f"✅ Found {len(onnx_files)} voice model(s)")
        for model in onnx_files[:3]:  # Show first 3
            print(f"   - {model.name}")
        
        return True
    
    @staticmethod
    def validate_directories() -> bool:
        """Validate and create required directories."""
        dirs = [
            settings.storage_dir,
            settings.storage_dir / "uploads",
            settings.storage_dir / "outputs",
            settings.storage_dir / "temp"
        ]
        
        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)
        
        print("✅ All required directories ready")
        return True
    
    @staticmethod
    def validate_python_dependencies() -> bool:
        """Validate critical Python dependencies."""
        critical_deps = [
            ("fastapi", "FastAPI web framework"),
            ("uvicorn", "ASGI server"),
            ("PyPDF2", "PDF text extraction"),
            ("fitz", "PyMuPDF for advanced PDF"),
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
            return False
        
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
        
        for check_name, passed in results.items():
            status = "✅ PASS" if passed else "⚠️  WARN"
            check_display = check_name.replace("_", " ").title()
            print(f"{status} {check_display}")
        
        print("-" * 60)
        
        total_checks = len(results)
        passed_checks = sum(results.values())
        print(f"Results: {passed_checks}/{total_checks} checks passed")
        
        if all(results.values()):
            print("🎉 All validations passed! Application ready.")
        elif passed_checks >= 3:
            print("⚠️  Some validations failed but app should work.")
        else:
            print("❌ Critical validations failed. Check errors above.")
