"""
Book splitting service that orchestrates chapter detection and file generation
"""
import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import json
import hashlib
from datetime import datetime
import logging

from app.services.detector import ChapterDetector, Chapter
from app.utils.file_naming import FileNamingService
from app.utils.text_cleaner import TextCleaner

logger = logging.getLogger(__name__)

@dataclass
class SplitResult:
    """Result of book splitting operation"""
    book_id: str
    book_title: str
    total_chapters: int
    chapters: List[Dict]  # Chapter metadata
    output_dir: str
    manifest_path: str
    estimated_total_duration_seconds: int

class BookSplitter:
    """
    Main service for splitting books into manageable chunks
    """
    
    def __init__(
        self,
        output_base_dir: str = "/tmp/tts_processing",
        max_chapter_duration_minutes: int = 30
    ):
        """
        Initialize book splitter
        
        Args:
            output_base_dir: Base directory for output files
            max_chapter_duration_minutes: Maximum duration per chapter
        """
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(parents=True, exist_ok=True)
        
        self.detector = ChapterDetector(max_chapter_duration_minutes)
        self.namer = FileNamingService()
        self.cleaner = TextCleaner()
    
    def split_book(
        self, 
        file_path: str, 
        file_type: str,
        book_title: Optional[str] = None,
        author: Optional[str] = None
    ) -> SplitResult:
        """
        Split a book into chapters and prepare for TTS processing
        
        Args:
            file_path: Path to the book file
            file_type: 'epub' or 'pdf'
            book_title: Optional book title override
            author: Optional author name
            
        Returns:
            SplitResult with all chapter information
        """
        # Generate unique book ID
        book_id = self._generate_book_id(file_path)
        
        # Extract metadata if not provided
        if not book_title:
            book_title = self._extract_book_title(file_path, file_type)
        
        # Detect chapters
        logger.info(f"Detecting chapters in {file_path}")
        chapters = self.detector.detect_chapters(file_path, file_type)
        logger.info(f"Found {len(chapters)} chapters")
        
        # Create output directory structure
        output_dir = self.output_base_dir / book_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process and save each chapter
        chapter_metadata = []
        total_duration = 0
        
        for chapter in chapters:
            # Clean text for TTS
            cleaned_content = self.cleaner.clean_for_tts(chapter.content)
            
            # Generate filename
            filename = self.namer.generate_chapter_filename(
                book_title=book_title,
                chapter_index=chapter.index,
                chapter_title=chapter.title,
                author=author
            )
            
            # Save chapter text
            chapter_path = output_dir / f"{filename}.txt"
            chapter_path.write_text(cleaned_content, encoding='utf-8')
            
            # Prepare metadata
            metadata = {
                'index': chapter.index,
                'title': chapter.title,
                'filename': filename,
                'text_file': str(chapter_path),
                'audio_file': None,  # Will be filled by TTS service
                'word_count': chapter.estimated_words,
                'estimated_duration_seconds': chapter.estimated_duration_seconds,
                'status': 'pending',
                'error': None
            }
            
            chapter_metadata.append(metadata)
            total_duration += chapter.estimated_duration_seconds
        
        # Create manifest file
        manifest = {
            'book_id': book_id,
            'book_title': book_title,
            'author': author,
            'source_file': os.path.basename(file_path),
            'file_type': file_type,
            'created_at': datetime.now().isoformat(),
            'total_chapters': len(chapters),
            'estimated_total_duration_seconds': total_duration,
            'chapters': chapter_metadata
        }
        
        manifest_path = output_dir / 'manifest.json'
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        
        return SplitResult(
            book_id=book_id,
            book_title=book_title,
            total_chapters=len(chapters),
            chapters=chapter_metadata,
            output_dir=str(output_dir),
            manifest_path=str(manifest_path),
            estimated_total_duration_seconds=total_duration
        )
    
    def _generate_book_id(self, file_path: str) -> str:
        """
        Generate unique book ID based on file content
        """
        hasher = hashlib.sha256()
        
        # Hash file content
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        
        # Add timestamp for uniqueness
        hasher.update(str(datetime.now().timestamp()).encode())
        
        return hasher.hexdigest()[:12]
    
    def _extract_book_title(self, file_path: str, file_type: str) -> str:
        """
        Extract book title from metadata or filename
        """
        # Try to get from file metadata
        if file_type.lower() == 'epub':
            try:
                import ebooklib
                from ebooklib import epub
                book = epub.read_epub(file_path)
                title = book.get_metadata('DC', 'title')
                if title and title[0]:
                    return title[0][0]
            except Exception as e:
                logger.warning(f"Could not extract EPUB metadata: {e}")
        
        elif file_type.lower() == 'pdf':
            try:
                import fitz
                doc = fitz.open(file_path)
                if doc.metadata and doc.metadata.get('title'):
                    title = doc.metadata['title']
                    doc.close()
                    return title
                doc.close()
            except Exception as e:
                logger.warning(f"Could not extract PDF metadata: {e}")
        
        # Fallback to filename
        return Path(file_path).stem
    
    def get_split_info(self, book_id: str) -> Optional[Dict]:
        """
        Get information about a previously split book
        """
        manifest_path = self.output_base_dir / book_id / 'manifest.json'
        
        if not manifest_path.exists():
            return None
        
        return json.loads(manifest_path.read_text())
    
    def cleanup_book(self, book_id: str) -> bool:
        """
        Clean up all files for a book
        """
        book_dir = self.output_base_dir / book_id
        
        if book_dir.exists():
            shutil.rmtree(book_dir)
            logger.info(f"Cleaned up book {book_id}")
            return True
        
        return False


class FileNamingService:
    """
    Service for generating consistent, sortable filenames
    """
    
    @staticmethod
    def sanitize_filename(text: str, max_length: int = 50) -> str:
        """
        Sanitize text for use in filename
        """
        # Remove special characters
        import re
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        text = re.sub(r'\s+', '_', text)
        text = text.strip('._')
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length].rsplit('_', 1)[0]
        
        return text or "untitled"
    
    def generate_chapter_filename(
        self,
        book_title: str,
        chapter_index: int,
        chapter_title: str,
        author: Optional[str] = None
    ) -> str:
        """
        Generate a sortable, descriptive filename for a chapter
        
        Format: [index]_[book]_[author]_[chapter]
        Example: 001_MobyDick_Melville_Chapter1_CallMeIshmael
        """
        parts = []
        
        # Index with zero padding for sorting
        parts.append(f"{chapter_index:03d}")
        
        # Book title
        parts.append(self.sanitize_filename(book_title, 30))
        
        # Author if provided
        if author:
            parts.append(self.sanitize_filename(author, 20))
        
        # Chapter title
        parts.append(self.sanitize_filename(chapter_title, 30))
        
        return "_".join(parts)
    
    def parse_chapter_filename(self, filename: str) -> Dict[str, str]:
        """
        Parse chapter filename back to components
        """
        # Remove extension
        name = Path(filename).stem
        parts = name.split('_')
        
        result = {
            'index': int(parts[0]) if parts[0].isdigit() else 0,
            'book_title': parts[1] if len(parts) > 1 else '',
        }
        
        # Check if author is included
        if len(parts) > 3:
            result['author'] = parts[2]
            result['chapter_title'] = '_'.join(parts[3:])
        else:
            result['author'] = None
            result['chapter_title'] = '_'.join(parts[2:]) if len(parts) > 2 else ''
        
        return result


class TextCleaner:
    """
    Text cleaning service for TTS preparation
    """
    
    def clean_for_tts(self, text: str) -> str:
        """
        Clean text for optimal TTS processing
        """
        import re
        
        # Remove multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove page numbers (common patterns)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^Page \d+\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'([.,!?;:])\s*', r'\1 ', text)
        
        # Remove excessive whitespace