"""File naming utilities for the audio book converter."""

import re
import hashlib
from pathlib import Path
from typing import Optional
from datetime import datetime


class FileNamingService:
    """Service for handling file naming and sanitization."""
    
    @staticmethod
    def sanitize_filename(filename: str, max_length: int = 255) -> str:
        """
        Sanitize a filename to be filesystem-safe.
        
        Args:
            filename: Original filename
            max_length: Maximum allowed length
            
        Returns:
            Sanitized filename
        """
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        
        # Ensure filename is not empty
        if not filename:
            filename = "unnamed"
        
        # Truncate if too long
        if len(filename) > max_length:
            name, ext = Path(filename).stem, Path(filename).suffix
            max_name_length = max_length - len(ext) - 1
            filename = name[:max_name_length] + ext
        
        return filename
    
    @staticmethod
    def generate_unique_filename(
        base_name: str,
        extension: str,
        directory: Path,
        timestamp: bool = True
    ) -> str:
        """
        Generate a unique filename in the given directory.
        
        Args:
            base_name: Base name for the file
            extension: File extension (with or without dot)
            directory: Target directory
            timestamp: Whether to include timestamp
            
        Returns:
            Unique filename
        """
        # Ensure extension starts with dot
        if not extension.startswith('.'):
            extension = f'.{extension}'
        
        # Sanitize base name
        base_name = FileNamingService.sanitize_filename(base_name)
        
        if timestamp:
            # Add timestamp for uniqueness
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{base_name}_{timestamp_str}{extension}"
        else:
            filename = f"{base_name}{extension}"
            
            # If file exists, add counter
            counter = 1
            while (directory / filename).exists():
                filename = f"{base_name}_{counter}{extension}"
                counter += 1
        
        return filename
    
    @staticmethod
    def get_output_filename(
        input_filename: str,
        voice_model: str,
        output_format: str = "wav"
    ) -> str:
        """
        Generate output filename based on input and voice model.
        
        Args:
            input_filename: Original input filename
            voice_model: Voice model used
            output_format: Output audio format
            
        Returns:
            Output filename
        """
        # Get base name without extension
        base_name = Path(input_filename).stem
        
        # Sanitize voice model name
        voice_short = voice_model.replace('/', '_').replace('.onnx', '')
        if len(voice_short) > 20:
            # Use hash if voice name is too long
            voice_short = hashlib.md5(voice_model.encode()).hexdigest()[:8]
        
        # Create output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_name = f"{base_name}_{voice_short}_{timestamp}.{output_format}"
        
        return FileNamingService.sanitize_filename(output_name)
    
    @staticmethod
    def get_chapter_filename(
        book_name: str,
        chapter_index: int,
        chapter_title: Optional[str] = None,
        format: str = "wav"
    ) -> str:
        """
        Generate filename for a chapter audio file.
        
        Args:
            book_name: Name of the book
            chapter_index: Chapter number
            chapter_title: Optional chapter title
            format: Audio format
            
        Returns:
            Chapter filename
        """
        book_name = FileNamingService.sanitize_filename(book_name)
        
        if chapter_title:
            chapter_title = FileNamingService.sanitize_filename(chapter_title)
            # Limit chapter title length
            if len(chapter_title) > 50:
                chapter_title = chapter_title[:50]
            filename = f"{book_name}_ch{chapter_index:03d}_{chapter_title}.{format}"
        else:
            filename = f"{book_name}_ch{chapter_index:03d}.{format}"
        
        return filename
