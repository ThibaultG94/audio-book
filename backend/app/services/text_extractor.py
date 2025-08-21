"""Text extraction from PDF and EPUB files."""

import unicodedata
from pathlib import Path
from PyPDF2 import PdfReader
from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup
from typing import Union

from app.core.exceptions import TextExtractionError


class TextExtractor:
    """Handles text extraction from various document formats."""
    
    @staticmethod
    def extract_from_file(file_path: Path) -> str:
        """
        Extract text from PDF or EPUB file.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text content
            
        Raises:
            TextExtractionError: If extraction fails
        """
        suffix = file_path.suffix.lower()
        
        try:
            if suffix == ".pdf":
                return TextExtractor._extract_from_pdf(file_path)
            elif suffix == ".epub":
                return TextExtractor._extract_from_epub(file_path)
            else:
                raise TextExtractionError(f"Unsupported file format: {suffix}")
        except Exception as e:
            raise TextExtractionError(f"Failed to extract text from {file_path}: {str(e)}")
    
    @staticmethod
    def _extract_from_pdf(file_path: Path) -> str:
        """Extract text from PDF file."""
        reader = PdfReader(str(file_path))
        text_parts = []
        
        for page in reader.pages:
            text = page.extract_text() or ""
            text_parts.append(text)
        
        return "\n".join(text_parts)
    
    @staticmethod
    def _extract_from_epub(file_path: Path) -> str:
        """Extract text from EPUB file."""
        book = epub.read_epub(str(file_path))
        text_chunks = []
        
        for item in book.get_items_of_type(ITEM_DOCUMENT):
            html_content = item.get_content().decode("utf-8", errors="ignore")
            text = BeautifulSoup(html_content, "lxml").get_text(" ", strip=True)
            text_chunks.append(text)
        
        return "\n".join(text_chunks)
