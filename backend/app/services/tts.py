"""
TTS Service with chunked processing and progress tracking
"""
import os
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import logging
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class ConversionStatus(Enum):
    """Status of a conversion job"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ConversionJob:
    """Represents a TTS conversion job"""
    job_id: str
    book_id: str
    book_title: str
    total_chapters: int
    chapters_completed: int = 0
    status: ConversionStatus = ConversionStatus.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    current_chapter: Optional[str] = None
    output_zip: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['status'] = self.status.value
        return data

class TTSService:
    """
    TTS conversion service with progress tracking and chunked processing
    """
    
    def __init__(
        self,
        model_path: str = "/models/piper/en_US-amy-medium.onnx",
        config_path: str = "/models/piper/en_US-amy-medium.onnx.json",
        output_format: str = "mp3",
        sample_rate: int = 22050,
        max_workers: int = 2
    ):
        """
        Initialize TTS service
        
        Args:
            model_path: Path to Piper model
            config_path: Path to Piper config
            output_format: Output audio format (wav/mp3)
            sample_rate: Sample rate for audio
            max_workers: Maximum parallel TTS workers
        """
        self.model_path = model_path
        self.config_path = config_path
        self.output_format = output_format
        self.sample_rate = sample_rate
        self.max_workers = max_workers
        
        # Job tracking
        self.jobs: Dict[str, ConversionJob] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Verify Piper installation
        self._verify_piper()
    
    def _verify_piper(self):
        """Verify Piper TTS is installed and accessible"""
        try:
            result = subprocess.run(
                ["piper", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("Piper TTS not properly installed")
            logger.info(f"Piper TTS version: {result.stdout.strip()}")
        except FileNotFoundError:
            raise RuntimeError("Piper TTS not found. Please install it first.")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Piper TTS timeout during verification")
    
    async def convert_book(
        self,
        book_id: str,
        manifest_path: str,
        progress_callback: Optional[Callable[[str, Dict], None]] = None
    ) -> ConversionJob:
        """
        Convert all chapters of a book to audio
        
        Args:
            book_id: Unique book identifier
            manifest_path: Path to book manifest JSON
            progress_callback: Optional callback for progress updates
            
        Returns:
            ConversionJob with results
        """
        # Load manifest
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Create job
        job_id = f"{book_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        job = ConversionJob(
            job_id=job_id,
            book_id=book_id,
            book_title=manifest['book_title'],
            total_chapters=manifest['total_chapters'],
            started_at=datetime.now().isoformat()
        )
        
        self.jobs[job_id] = job
        job.status = ConversionStatus.PROCESSING
        
        # Process chapters
        try:
            await self._process_chapters(job, manifest, progress_callback)
            
            # Create final ZIP
            if job.chapters_completed > 0:
                job.output_zip = await self._create_archive(job, manifest)
            
            job.status = ConversionStatus.COMPLETED
            job.completed_at = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Conversion failed for job {job_id}: {e}")
            job.status = ConversionStatus.FAILED
            job.error = str(e)
        
        finally:
            # Update manifest with results
            self._update_manifest(manifest_path, manifest)
        
        return job
    
    async def _process_chapters(
        self,
        job: ConversionJob,
        manifest: Dict,
        progress_callback: Optional[Callable]
    ):
        """
        Process all chapters with parallel execution
        """
        chapters = manifest['chapters']
        output_dir = Path(manifest_path).parent
        
        # Create futures for parallel processing
        futures = []
        
        loop = asyncio.get_event_loop()
        
        for chapter in chapters:
            # Skip already processed chapters
            if chapter['status'] == 'completed':
                job.chapters_completed += 1
                continue
            
            future = loop.run_in_executor(
                self.executor,
                self._convert_chapter,
                chapter,
                output_dir
            )
            futures.append((future, chapter))
        
        # Process futures as they complete
        for future, chapter in futures:
            try:
                job.current_chapter = chapter['title']
                
                # Send progress update
                if progress_callback:
                    progress_callback(job.job_id, {
                        'status': 'processing',
                        'current_chapter': chapter['title'],
                        'progress': job.chapters_completed / job.total_chapters
                    })
                
                # Wait for conversion
                audio_path = await future
                
                # Update chapter metadata
                chapter['audio_file'] = str(audio_path)
                chapter['status'] = 'completed'
                chapter['converted_at'] = datetime.now().isoformat()
                
                job.chapters_completed += 1
                
                # Send completion update
                if progress_callback:
                    progress_callback(job.job_id, {
                        'status': 'chapter_completed',
                        'chapter': chapter['title'],
                        'audio_file': str(audio_path),
                        'progress': job.chapters_completed / job.total_chapters
                    })
                
            except Exception as e:
                logger.error(f"Failed to convert chapter {chapter['title']}: {e}")
                chapter['status'] = 'failed'
                chapter['error'] = str(e)
                
                # Continue with other chapters
                continue
    
    def _convert_chapter(self, chapter: Dict, output_dir: Path) -> Path:
        """
        Convert a single chapter to audio using Piper
        
        Args:
            chapter: Chapter metadata
            output_dir: Output directory
            
        Returns:
            Path to generated audio file
        """
        text_file = chapter['text_file']
        base_name = Path(text_file).stem
        
        # Generate output filename
        if self.output_format == 'mp3':
            # First generate WAV, then convert to MP3
            wav_path = output_dir / f"{base_name}.wav"
            mp3_path = output_dir / f"{base_name}.mp3"
            output_path = mp3_path
        else:
            wav_path = output_dir / f"{base_name}.wav"
            output_path = wav_path
        
        # Run Piper TTS
        logger.info(f"Converting {chapter['title']} to audio")
        
        with open(text_file, 'r') as f:
            text = f.read()
        
        # Piper command
        cmd = [
            "piper",
            "--model", self.model_path,
            "--config", self.config_path,
            "--output_file", str(wav_path)
        ]
        
        # Run conversion
        result = subprocess.run(
            cmd,
            input=text,
            text=True,
            capture_output=True,
            timeout=300  # 5 minute timeout per chapter
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Piper TTS failed: {result.stderr}")
        
        # Convert to MP3 if needed
        if self.output_format == 'mp3' and wav_path.exists():
            self._convert_to_mp3(wav_path, mp3_path)
            wav_path.unlink()  # Remove WAV file
        
        return output_path
    
    def _convert_to_mp3(self, wav_path: Path, mp3_path: Path):
        """
        Convert WAV to MP3 using ffmpeg
        """
        cmd = [
            "ffmpeg",
            "-i", str(wav_path),
            "-acodec", "libmp3lame",
            "-ab", "128k",
            "-y",  # Overwrite output
            str(mp3_path)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=60
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg conversion failed: {result.stderr}")
    
    async def _create_archive(self, job: ConversionJob, manifest: Dict) -> str:
        """
        Create ZIP archive with all audio files
        """
        output_dir = Path(manifest_path).parent
        zip_path = output_dir / f"{job.book_title.replace(' ', '_')}_audiobook.zip"
        
        logger.info(f"Creating archive: {zip_path}")
        
        # Create ZIP file
        import zipfile
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add all audio files
            for chapter in manifest['chapters']:
                if chapter['status'] == 'completed' and chapter['audio_file']:
                    audio_path = Path(chapter['audio_file'])
                    if audio_path.exists():
                        arc_name = f"{chapter['filename']}.{self.output_format}"
                        zf.write(audio_path, arc_name)
            
            # Add manifest
            manifest_json = json.dumps(manifest, indent=2)
            zf.writestr('manifest.json', manifest_json)
            
            # Add README
            readme = self._generate_readme(job, manifest)
            zf.writestr('README.txt', readme)
        
        return str(zip_path)
    
    def _generate_readme(self, job: ConversionJob, manifest: Dict) -> str:
        """
        Generate README for audiobook archive
        """
        readme = f"""
{manifest['book_title']} - Audiobook
{'=' * 50}

Book: {manifest['book_title']}
Author: {manifest.get('author', 'Unknown')}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Total Chapters: {job.chapters_completed}/{job.total_chapters}
Format: {self.output_format.upper()}

Chapter List:
-------------
"""
        
        for chapter in manifest['chapters']:
            if chapter['status'] == 'completed':
                duration_min = chapter['estimated_duration_seconds'] // 60
                duration_sec = chapter['estimated_duration_seconds'] % 60
                readme += f"  {chapter['index']+1:3d}. {chapter['title']} ({duration_min}:{duration_sec:02d})\n"
        
        readme += """

Notes:
------
- Files are numbered for proper playback order
- Use any audio player that supports playlists
- Generated using Piper TTS

Enjoy your audiobook!
"""
        
        return readme
    
    def _update_manifest(self, manifest_path: str, manifest: Dict):
        """
        Update manifest file with conversion results
        """
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """
        Get current status of a conversion job
        """
        job = self.jobs.get(job_id)
        if job:
            return job.to_dict()
        return None
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a running job
        """
        job = self.jobs.get(job_id)
        if job and job.status == ConversionStatus.PROCESSING:
            job.status = ConversionStatus.CANCELLED
            # Note: Actual cancellation of running threads would require more complex handling
            return True
        return False
    
    def cleanup_job(self, job_id: str):
        """
        Clean up job data and temporary files
        """
        if job_id in self.jobs:
            job = self.jobs[job_id]
            # Clean up temp files if needed
            del self.jobs[job_id]