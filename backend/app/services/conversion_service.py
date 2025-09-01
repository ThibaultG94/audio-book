"""Complete conversion service for audiobook generation."""

import asyncio
import logging
import uuid
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime

from app.services.text_extractor import TextExtractor
from app.services.text_processor import TextProcessor
from app.services.tts_engine import TTSEngine
from app.services.audio_processor import AudioProcessor
from app.core.config import settings

logger = logging.getLogger(__name__)


class ConversionService:
    """Service for managing complete audiobook conversion pipeline."""
    
    def __init__(self):
        self.text_extractor = TextExtractor()
        self.text_processor = TextProcessor()
        self.tts_engine = TTSEngine()
        self.audio_processor = AudioProcessor()
        self.conversions: Dict[str, Dict[str, Any]] = {}
        
    async def start_conversion(
        self,
        file_path: Path,
        voice_model: str,
        tts_params: Optional[Dict[str, float]] = None,
        output_format: str = "wav"
    ) -> str:
        """Start a new conversion job.
        
        Args:
            file_path: Path to uploaded PDF/EPUB file
            voice_model: Path to voice model
            tts_params: TTS parameters (speed, expressiveness, etc.)
            output_format: Output audio format (wav/mp3)
            
        Returns:
            str: Job ID for tracking conversion progress
        """
        job_id = str(uuid.uuid4())
        
        # Initialize conversion tracking
        self.conversions[job_id] = {
            "id": job_id,
            "status": "initializing",
            "progress": 0,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "file_path": str(file_path),
            "voice_model": voice_model,
            "output_format": output_format,
            "error": None,
            "steps": {
                "extraction": {"status": "pending", "progress": 0},
                "processing": {"status": "pending", "progress": 0},
                "synthesis": {"status": "pending", "progress": 0},
                "finalization": {"status": "pending", "progress": 0}
            },
            "output_file": None,
            "duration_estimate": None,
            "chapters": []
        }
        
        # Start async conversion
        asyncio.create_task(self._run_conversion(job_id, file_path, voice_model, tts_params, output_format))
        
        return job_id
    
    async def _run_conversion(
        self,
        job_id: str,
        file_path: Path,
        voice_model: str,
        tts_params: Optional[Dict[str, float]],
        output_format: str
    ):
        """Run the complete conversion pipeline."""
        try:
            # Step 1: Extract text from document
            await self._update_status(job_id, "extracting", 10)
            self.conversions[job_id]["steps"]["extraction"]["status"] = "in_progress"
            
            text_content = await asyncio.to_thread(
                self.text_extractor.extract_text,
                file_path
            )
            
            if not text_content.strip():
                raise ValueError("No text content found in document")
            
            self.conversions[job_id]["steps"]["extraction"]["status"] = "completed"
            self.conversions[job_id]["steps"]["extraction"]["progress"] = 100
            
            # Step 2: Process and clean text
            await self._update_status(job_id, "processing", 30)
            self.conversions[job_id]["steps"]["processing"]["status"] = "in_progress"
            
            processed_text = self.text_processor.clean_text(text_content)
            chunks = self.text_processor.chunk_text(processed_text)
            
            self.conversions[job_id]["chapters"] = [
                {
                    "id": f"chunk_{i}",
                    "title": f"Section {i+1}",
                    "text_length": len(chunk),
                    "status": "pending"
                }
                for i, chunk in enumerate(chunks)
            ]
            
            self.conversions[job_id]["steps"]["processing"]["status"] = "completed"
            self.conversions[job_id]["steps"]["processing"]["progress"] = 100
            
            # Step 3: Generate audio for each chunk
            await self._update_status(job_id, "synthesizing", 50)
            self.conversions[job_id]["steps"]["synthesis"]["status"] = "in_progress"
            
            audio_files = []
            total_chunks = len(chunks)
            
            for i, chunk in enumerate(chunks):
                # Update chapter status
                self.conversions[job_id]["chapters"][i]["status"] = "processing"
                
                # Generate audio
                audio_data = await self.tts_engine.synthesize(
                    text=chunk,
                    voice_model_path=voice_model,
                    **tts_params if tts_params else {}
                )
                
                # Save chunk audio
                chunk_file = settings.TEMP_DIR / f"{job_id}_chunk_{i}.wav"
                chunk_file.write_bytes(audio_data)
                audio_files.append(chunk_file)
                
                # Update progress
                progress = 50 + int((i + 1) / total_chunks * 40)
                await self._update_status(job_id, "synthesizing", progress)
                
                self.conversions[job_id]["chapters"][i]["status"] = "completed"
                self.conversions[job_id]["chapters"][i]["audio_file"] = str(chunk_file)
            
            self.conversions[job_id]["steps"]["synthesis"]["status"] = "completed"
            self.conversions[job_id]["steps"]["synthesis"]["progress"] = 100
            
            # Step 4: Combine audio files
            await self._update_status(job_id, "finalizing", 90)
            self.conversions[job_id]["steps"]["finalization"]["status"] = "in_progress"
            
            output_file = settings.OUTPUT_DIR / f"{job_id}.{output_format}"
            
            await asyncio.to_thread(
                self.audio_processor.combine_audio_files,
                audio_files,
                output_file,
                pause_duration=settings.DEFAULT_PAUSE_BETWEEN_BLOCKS
            )
            
            # Clean up temporary files
            for audio_file in audio_files:
                audio_file.unlink(missing_ok=True)
            
            self.conversions[job_id]["steps"]["finalization"]["status"] = "completed"
            self.conversions[job_id]["steps"]["finalization"]["progress"] = 100
            
            # Update final status
            self.conversions[job_id]["status"] = "completed"
            self.conversions[job_id]["progress"] = 100
            self.conversions[job_id]["completed_at"] = datetime.utcnow().isoformat()
            self.conversions[job_id]["output_file"] = str(output_file)
            
            # Calculate duration estimate
            duration = await self.tts_engine.estimate_duration(
                processed_text,
                tts_params.get("length_scale", 1.0) if tts_params else 1.0,
                tts_params.get("sentence_silence", 0.35) if tts_params else 0.35
            )
            self.conversions[job_id]["duration_estimate"] = duration
            
            logger.info(f"Conversion {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Conversion {job_id} failed: {str(e)}")
            self.conversions[job_id]["status"] = "failed"
            self.conversions[job_id]["error"] = str(e)
            
            # Mark current step as failed
            for step in self.conversions[job_id]["steps"].values():
                if step["status"] == "in_progress":
                    step["status"] = "failed"
    
    async def _update_status(self, job_id: str, status: str, progress: int):
        """Update conversion status and progress."""
        if job_id in self.conversions:
            self.conversions[job_id]["status"] = status
            self.conversions[job_id]["progress"] = progress
    
    def get_conversion_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a conversion job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            dict: Conversion status information or None if not found
        """
        return self.conversions.get(job_id)
    
    def list_conversions(self) -> List[Dict[str, Any]]:
        """List all conversion jobs.
        
        Returns:
            list: All conversion jobs with their status
        """
        return list(self.conversions.values())
    
    async def cancel_conversion(self, job_id: str) -> bool:
        """Cancel an ongoing conversion.
        
        Args:
            job_id: Job identifier
            
        Returns:
            bool: True if cancelled successfully
        """
        if job_id in self.conversions:
            self.conversions[job_id]["status"] = "cancelled"
            self.conversions[job_id]["error"] = "Conversion cancelled by user"
            return True
        return False


# Singleton instance
conversion_service = ConversionService()