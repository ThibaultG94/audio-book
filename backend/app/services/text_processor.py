"""Text cleaning and chunking for TTS processing."""

import re
import unicodedata
from typing import Generator


class TextProcessor:
    """Handles text cleaning and chunking for optimal TTS processing."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text for TTS processing.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned and normalized text
        """
        # Unicode normalization - decompose then remove combining characters
        text = unicodedata.normalize("NFKD", text)
        text = "".join(c for c in text if not unicodedata.combining(c))
        
        # Clean up whitespace
        text = re.sub(r"[ \t]+", " ", text)  # Multiple spaces/tabs -> single space
        text = re.sub(r"\n{2,}", "\n\n", text)  # Multiple newlines -> double newline
        
        return text.strip()
    
    @staticmethod
    def chunk_paragraphs(text: str, max_chars: int = 1500) -> Generator[str, None, None]:
        """
        Split text into chunks suitable for TTS processing.
        
        Args:
            text: Cleaned text to chunk
            max_chars: Maximum characters per chunk
            
        Yields:
            Text chunks ready for TTS processing
        """
        # Split into paragraphs (double newline separated)
        paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
        
        current_chunk = []
        current_length = 0
        
        for paragraph in paragraphs:
            paragraph_length = len(paragraph)
            
            # If adding this paragraph would exceed limit and we have content
            if current_length + paragraph_length > max_chars and current_chunk:
                yield "\n".join(current_chunk)
                current_chunk = [paragraph]
                current_length = paragraph_length
            else:
                current_chunk.append(paragraph)
                current_length += paragraph_length
        
        # Yield remaining content
        if current_chunk:
            yield "\n".join(current_chunk)