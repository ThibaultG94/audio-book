"""Text extraction from PDF and EPUB files."""

import unicodedata
from pathlib import Path
from PyPDF2 import PdfReader
from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup
from typing import Union
import zipfile
import xml.etree.ElementTree as ET

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
            elif suffix == ".txt":
                return TextExtractor._extract_from_txt(file_path)
            elif suffix == ".docx":
                return TextExtractor._extract_from_docx(file_path)
            elif suffix == ".rtf":
                return TextExtractor._extract_from_rtf(file_path)
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
            text = BeautifulSoup(html_content, "xml").get_text(" ", strip=True)
            text_chunks.append(text)
        
        return "\n".join(text_chunks)
    
    @staticmethod
    def _extract_from_txt(file_path: Path) -> str:
        """Extract text from TXT file."""
        try:
            # Try UTF-8 first, then fallback to other encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        return file.read()
                except UnicodeDecodeError:
                    continue
            raise TextExtractionError(f"Could not decode text file with any common encoding")
        except Exception as e:
            raise TextExtractionError(f"Failed to read TXT file: {str(e)}")
    
    @staticmethod
    def _extract_from_docx(file_path: Path) -> str:
        """Extract text from DOCX file."""
        try:
            text_parts = []
            with zipfile.ZipFile(file_path, 'r') as docx:
                # Read document.xml which contains the main text
                with docx.open('word/document.xml') as doc_xml:
                    root = ET.parse(doc_xml).getroot()
                    
                    # Define namespace
                    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                    
                    # Extract text from all text elements
                    for text_elem in root.findall('.//w:t', ns):
                        if text_elem.text:
                            text_parts.append(text_elem.text)
            
            return "\n".join(text_parts) if text_parts else ""
        except Exception as e:
            raise TextExtractionError(f"Failed to extract from DOCX: {str(e)}")
    
    @staticmethod 
    def _extract_from_rtf(file_path: Path) -> str:
        """Extract text from RTF file (simple approach)."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                rtf_content = file.read()
            
            # Very basic RTF parsing - remove control words and groups
            import re
            # Remove RTF control words (\\word)
            text = re.sub(r'\\[a-z]+\d*', '', rtf_content)
            # Remove RTF control symbols
            text = re.sub(r'\\[^a-z]', '', text)
            # Remove RTF groups {}
            text = re.sub(r'[{}]', '', text)
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
        except Exception as e:
            raise TextExtractionError(f"Failed to extract from RTF: {str(e)}")
