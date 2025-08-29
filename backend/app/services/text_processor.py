"""Text cleaning and chunking for TTS processing."""

import re
import unicodedata
from typing import Generator


class TextProcessor:
    """Handles text cleaning and chunking for optimal TTS processing."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text for TTS processing, ensuring Piper compatibility.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned and normalized text safe for Piper TTS
        """
        # Step 1: Use NFC normalization (composed form) to avoid decomposed characters
        text = unicodedata.normalize("NFC", text)
        
        # Step 2: Remove problematic characters that cause Piper issues
        # Remove combining diacritical marks that Piper can't handle
        text = "".join(c for c in text if unicodedata.category(c) != 'Mn')
        
        # Step 3: Replace specific problematic characters
        replacements = {
            # Remove phonetic symbols that cause Piper errors
            '\u0303': '',  # COMBINING TILDE (phonetic nasalization)
            '\u0301': '',  # COMBINING ACUTE ACCENT
            '\u0300': '',  # COMBINING GRAVE ACCENT  
            '\u0302': '',  # COMBINING CIRCUMFLEX ACCENT
            '\u030C': '',  # COMBINING CARON
            '\u0327': '',  # COMBINING CEDILLA
            # Remove zero-width characters
            '\u200B': '',  # ZERO WIDTH SPACE
            '\u200C': '',  # ZERO WIDTH NON-JOINER
            '\u200D': '',  # ZERO WIDTH JOINER
            '\uFEFF': '',  # ZERO WIDTH NO-BREAK SPACE
            # Replace problematic quotation marks
            '"': '"',      # LEFT DOUBLE QUOTATION MARK
            '"': '"',      # RIGHT DOUBLE QUOTATION MARK
            ''': "'",      # LEFT SINGLE QUOTATION MARK
            ''': "'",      # RIGHT SINGLE QUOTATION MARK
            # Replace problematic dashes
            '—': '-',      # EM DASH
            '–': '-',      # EN DASH
            # Replace ellipsis
            '…': '...',    # HORIZONTAL ELLIPSIS
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Step 4: Keep only safe characters for French TTS
        # Allow basic Latin, French accented characters, digits, punctuation, and whitespace
        safe_pattern = r'[a-zA-Z0-9àáâäçèéêëïîôöùúûüÿÀÁÂÄÇÈÉÊËÏÎÔÖÙÚÛÜŸ\s\.,!?;:()\-\'"«»\n]'
        text = ''.join(c for c in text if re.match(safe_pattern, c))
        
        # Step 5: Clean up whitespace
        text = re.sub(r"[ \t]+", " ", text)  # Multiple spaces/tabs -> single space
        text = re.sub(r"\n{2,}", "\n\n", text)  # Multiple newlines -> double newline
        text = re.sub(r"^\s+|\s+$", "", text, flags=re.MULTILINE)  # Trim lines
        
        return text.strip()
    
    @staticmethod
    def chunk_paragraphs(text: str, max_chars: int = 800) -> Generator[str, None, None]:
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