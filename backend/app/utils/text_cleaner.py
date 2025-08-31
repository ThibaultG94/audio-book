"""Text cleaning utilities for audio book processing."""

import re
import unicodedata
from typing import List, Optional, Tuple
from bs4 import BeautifulSoup


class TextCleaner:
    """Service for cleaning and normalizing text from various sources."""
    
    # Common replacements for better TTS pronunciation
    ABBREVIATIONS = {
        "Mr.": "Mister",
        "Mrs.": "Missus",
        "Ms.": "Miss",
        "Dr.": "Doctor",
        "Jr.": "Junior",
        "Sr.": "Senior",
        "Co.": "Company",
        "Inc.": "Incorporated",
        "Ltd.": "Limited",
        "St.": "Street",
        "Ave.": "Avenue",
        "etc.": "et cetera",
        "vs.": "versus",
        "e.g.": "for example",
        "i.e.": "that is",
    }
    
    # Characters to remove for cleaner speech
    REMOVE_CHARS = r'[\[\]{}()<>«»„"‟"'']'
    
    @staticmethod
    def clean_text(text: str, 
                   preserve_paragraphs: bool = True,
                   expand_abbreviations: bool = True,
                   remove_urls: bool = True,
                   normalize_whitespace: bool = True) -> str:
        """
        Clean and normalize text for TTS processing.
        
        Args:
            text: Raw text to clean
            preserve_paragraphs: Keep paragraph breaks
            expand_abbreviations: Replace abbreviations with full words
            remove_urls: Remove URLs from text
            normalize_whitespace: Normalize spacing
            
        Returns:
            Cleaned text ready for TTS
        """
        if not text:
            return ""
        
        # Remove HTML if present
        text = TextCleaner.remove_html_tags(text)
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        # Remove URLs
        if remove_urls:
            text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # Expand abbreviations for better pronunciation
        if expand_abbreviations:
            for abbr, full in TextCleaner.ABBREVIATIONS.items():
                text = text.replace(abbr, full)
                text = text.replace(abbr.upper(), full.upper())
        
        # Remove or replace special characters
        text = re.sub(TextCleaner.REMOVE_CHARS, '', text)
        
        # Replace quotes with standard ones
        text = re.sub(r'[""„‟]', '"', text)
        text = re.sub(r"[''`]", "'", text)
        
        # Handle dashes and hyphens
        text = re.sub(r'—|–', ' - ', text)
        
        # Remove page numbers and references
        text = re.sub(r'\[Page \d+\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
        
        # Normalize whitespace
        if normalize_whitespace:
            if preserve_paragraphs:
                # Keep paragraph breaks (double newlines)
                paragraphs = text.split('\n\n')
                paragraphs = [' '.join(p.split()) for p in paragraphs]
                text = '\n\n'.join(p for p in paragraphs if p.strip())
            else:
                text = ' '.join(text.split())
        
        return text.strip()
    
    @staticmethod
    def remove_html_tags(text: str) -> str:
        """Remove HTML tags from text."""
        try:
            soup = BeautifulSoup(text, 'html.parser')
            # Get text and preserve some structure
            text = soup.get_text(separator=' ', strip=True)
        except Exception:
            # If parsing fails, do basic regex cleanup
            text = re.sub(r'<[^>]+>', ' ', text)
        
        return text
    
    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """
        Split text into sentences for TTS processing.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Pattern for sentence boundaries
        sentence_endings = r'[.!?]+'
        
        # Split on sentence endings but keep the punctuation
        sentences = re.split(f'({sentence_endings})', text)
        
        # Reconstruct sentences with their punctuation
        result = []
        for i in range(0, len(sentences)-1, 2):
            if i+1 < len(sentences):
                sentence = sentences[i] + sentences[i+1]
                sentence = sentence.strip()
                if sentence:
                    result.append(sentence)
        
        # Handle last sentence if no ending punctuation
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            result.append(sentences[-1].strip())
        
        return result
    
    @staticmethod
    def prepare_for_tts(text: str, 
                       max_chunk_size: int = 1500,
                       add_pauses: bool = True) -> List[str]:
        """
        Prepare text chunks optimized for TTS processing.
        
        Args:
            text: Cleaned text
            max_chunk_size: Maximum characters per chunk
            add_pauses: Add pause markers for natural speech
            
        Returns:
            List of text chunks ready for TTS
        """
        # Clean the text first
        text = TextCleaner.clean_text(text)
        
        # Split into sentences
        sentences = TextCleaner.split_into_sentences(text)
        
        # Group sentences into chunks
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_len = len(sentence)
            
            # If single sentence is too long, split it
            if sentence_len > max_chunk_size:
                # Save current chunk if any
                if current_chunk:
                    chunk_text = ' '.join(current_chunk)
                    if add_pauses:
                        chunk_text = TextCleaner.add_speech_pauses(chunk_text)
                    chunks.append(chunk_text)
                    current_chunk = []
                    current_size = 0
                
                # Split long sentence by commas or semicolons
                parts = re.split(r'[,;]', sentence)
                for part in parts:
                    part = part.strip()
                    if part:
                        if add_pauses:
                            part = TextCleaner.add_speech_pauses(part)
                        chunks.append(part)
            
            # Add to current chunk if it fits
            elif current_size + sentence_len + 1 <= max_chunk_size:
                current_chunk.append(sentence)
                current_size += sentence_len + 1
            
            # Start new chunk
            else:
                if current_chunk:
                    chunk_text = ' '.join(current_chunk)
                    if add_pauses:
                        chunk_text = TextCleaner.add_speech_pauses(chunk_text)
                    chunks.append(chunk_text)
                
                current_chunk = [sentence]
                current_size = sentence_len
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if add_pauses:
                chunk_text = TextCleaner.add_speech_pauses(chunk_text)
            chunks.append(chunk_text)
        
        return chunks
    
    @staticmethod
    def add_speech_pauses(text: str) -> str:
        """
        Add natural pause markers for TTS.
        
        Args:
            text: Input text
            
        Returns:
            Text with pause markers
        """
        # Add small pauses after commas
        text = re.sub(r',(\s+)', r',\1... ', text)
        
        # Add longer pauses after periods, questions, exclamations
        text = re.sub(r'([.!?])(\s+)', r'\1\2... ... ', text)
        
        # Add pauses around dashes
        text = re.sub(r'\s*-\s*', ' ... - ... ', text)
        
        # Clean up multiple pauses
        text = re.sub(r'(\.\.\.\s*){3,}', '... ... ', text)
        
        return text
    
    @staticmethod
    def remove_footnotes(text: str) -> str:
        """Remove footnote references from text."""
        # Remove [1], [2], etc.
        text = re.sub(r'\[\d+\]', '', text)
        # Remove superscript numbers (if preserved as ^1, ^2, etc.)
        text = re.sub(r'\^\d+', '', text)
        # Remove (Note 1), (Note 2), etc.
        text = re.sub(r'\(Note\s+\d+\)', '', text, flags=re.IGNORECASE)
        
        return text
    
    @staticmethod
    def normalize_numbers(text: str) -> str:
        """
        Convert numbers to words for better TTS pronunciation.
        
        Args:
            text: Input text
            
        Returns:
            Text with normalized numbers
        """
        # This is a simplified version - for production, use a library like num2words
        
        # Convert common years
        text = re.sub(r'\b(19|20)(\d{2})\b', 
                     lambda m: f"{m.group(1)} {m.group(2)}", text)
        
        # Convert percentages
        text = re.sub(r'(\d+)%', r'\1 percent', text)
        
        # Convert currency (simplified)
        text = re.sub(r'\$(\d+)', r'\1 dollars', text)
        text = re.sub(r'€(\d+)', r'\1 euros', text)
        text = re.sub(r'£(\d+)', r'\1 pounds', text)
        
        return text
