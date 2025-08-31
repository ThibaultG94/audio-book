"""
Chapter detection service for EPUB and PDF files
"""
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import ebooklib
from ebooklib import epub
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

@dataclass
class Chapter:
    """Represents a book chapter"""
    index: int
    title: str
    content: str
    start_page: Optional[int] = None
    end_page: Optional[int] = None
    estimated_words: int = 0
    estimated_duration_seconds: int = 0  # Based on avg reading speed

class ChapterDetector:
    """
    Detects and extracts chapters from EPUB and PDF files
    """
    
    # Common chapter patterns
    CHAPTER_PATTERNS = [
        r'chapter\s+\d+',
        r'chapitre\s+\d+',  # French
        r'part\s+\d+',
        r'section\s+\d+',
        r'^\d+\.',
        r'^\d+\s',
        r'^[IVXLCDM]+\.',  # Roman numerals
    ]
    
    # Average words per minute for TTS
    TTS_WPM = 150
    
    def __init__(self, max_chapter_duration_minutes: int = 30):
        """
        Initialize detector with max chapter duration
        
        Args:
            max_chapter_duration_minutes: Maximum duration per chapter in minutes
        """
        self.max_words_per_chapter = max_chapter_duration_minutes * self.TTS_WPM
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.CHAPTER_PATTERNS]
    
    def detect_chapters(self, file_path: str, file_type: str) -> List[Chapter]:
        """
        Main entry point for chapter detection
        
        Args:
            file_path: Path to the book file
            file_type: 'epub' or 'pdf'
            
        Returns:
            List of detected chapters
        """
        if file_type.lower() == 'epub':
            return self._detect_epub_chapters(file_path)
        elif file_type.lower() == 'pdf':
            return self._detect_pdf_chapters(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _detect_epub_chapters(self, file_path: str) -> List[Chapter]:
        """
        Extract chapters from EPUB file
        """
        chapters = []
        book = epub.read_epub(file_path)
        
        # Try to use TOC first
        toc = book.toc
        if toc:
            logger.info(f"Found {len(toc)} TOC entries")
            chapters = self._extract_epub_from_toc(book, toc)
        
        # Fallback to content analysis
        if not chapters:
            logger.info("No TOC found, analyzing content structure")
            chapters = self._extract_epub_by_content(book)
        
        # If still no chapters, treat entire book as one
        if not chapters:
            logger.warning("No chapters detected, treating as single document")
            all_text = self._extract_all_epub_text(book)
            chapters = self._split_by_size(all_text, "Full Book")
        
        return self._post_process_chapters(chapters)
    
    def _extract_epub_from_toc(self, book: epub.EpubBook, toc: List) -> List[Chapter]:
        """
        Extract chapters using EPUB table of contents
        """
        chapters = []
        items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
        
        for idx, entry in enumerate(toc):
            if isinstance(entry, tuple):
                # Nested TOC structure
                title = entry[0].title if hasattr(entry[0], 'title') else f"Chapter {idx + 1}"
                href = entry[0].href if hasattr(entry[0], 'href') else None
            else:
                title = entry.title if hasattr(entry, 'title') else f"Chapter {idx + 1}"
                href = entry.href if hasattr(entry, 'href') else None
            
            if href:
                # Find corresponding content
                content = self._get_epub_content_by_href(book, href, items)
                if content:
                    chapters.append(Chapter(
                        index=idx,
                        title=title,
                        content=content,
                        estimated_words=len(content.split())
                    ))
        
        return chapters
    
    def _extract_epub_by_content(self, book: epub.EpubBook) -> List[Chapter]:
        """
        Extract chapters by analyzing content structure
        """
        chapters = []
        current_chapter = None
        chapter_index = 0
        
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            content = item.get_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()
            
            # Look for chapter markers
            for heading in soup.find_all(['h1', 'h2', 'h3']):
                heading_text = heading.get_text().strip()
                if self._is_chapter_heading(heading_text):
                    # Save previous chapter
                    if current_chapter:
                        chapters.append(current_chapter)
                    
                    # Start new chapter
                    current_chapter = Chapter(
                        index=chapter_index,
                        title=heading_text,
                        content="",
                        estimated_words=0
                    )
                    chapter_index += 1
            
            # Add content to current chapter
            if current_chapter:
                current_chapter.content += text + "\n"
                current_chapter.estimated_words = len(current_chapter.content.split())
            elif not chapters:
                # No chapter found yet, create first one
                current_chapter = Chapter(
                    index=0,
                    title="Chapter 1",
                    content=text,
                    estimated_words=len(text.split())
                )
                chapter_index = 1
        
        # Don't forget last chapter
        if current_chapter:
            chapters.append(current_chapter)
        
        return chapters
    
    def _detect_pdf_chapters(self, file_path: str) -> List[Chapter]:
        """
        Extract chapters from PDF file
        """
        chapters = []
        doc = fitz.open(file_path)
        
        # Try to use PDF outline (bookmarks)
        toc = doc.get_toc()
        if toc:
            logger.info(f"Found {len(toc)} TOC entries in PDF")
            chapters = self._extract_pdf_from_toc(doc, toc)
        
        # Fallback to content analysis
        if not chapters:
            logger.info("No TOC found in PDF, analyzing content")
            chapters = self._extract_pdf_by_content(doc)
        
        # If still no chapters, split by size
        if not chapters:
            logger.warning("No chapters detected in PDF, splitting by size")
            all_text = ""
            for page in doc:
                all_text += page.get_text() + "\n"
            chapters = self._split_by_size(all_text, doc.metadata.get('title', 'Document'))
        
        doc.close()
        return self._post_process_chapters(chapters)
    
    def _extract_pdf_from_toc(self, doc: fitz.Document, toc: List) -> List[Chapter]:
        """
        Extract chapters using PDF table of contents
        """
        chapters = []
        
        for idx, entry in enumerate(toc):
            level, title, page_num = entry
            
            # Only use top-level entries as chapters
            if level == 1:
                # Find end page (next chapter or end of doc)
                end_page = doc.page_count
                for next_entry in toc[idx + 1:]:
                    if next_entry[0] == 1:
                        end_page = next_entry[2] - 1
                        break
                
                # Extract text from pages
                content = ""
                for page_idx in range(page_num - 1, min(end_page, doc.page_count)):
                    page = doc[page_idx]
                    content += page.get_text() + "\n"
                
                chapters.append(Chapter(
                    index=len(chapters),
                    title=title,
                    content=content,
                    start_page=page_num,
                    end_page=end_page,
                    estimated_words=len(content.split())
                ))
        
        return chapters
    
    def _extract_pdf_by_content(self, doc: fitz.Document) -> List[Chapter]:
        """
        Extract chapters by analyzing PDF content
        """
        chapters = []
        current_chapter = None
        chapter_index = 0
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            lines = text.split('\n')
            
            for line in lines[:10]:  # Check first 10 lines for chapter headings
                if self._is_chapter_heading(line):
                    # Save previous chapter
                    if current_chapter:
                        current_chapter.end_page = page_num
                        chapters.append(current_chapter)
                    
                    # Start new chapter
                    current_chapter = Chapter(
                        index=chapter_index,
                        title=line.strip(),
                        content="",
                        start_page=page_num + 1,
                        estimated_words=0
                    )
                    chapter_index += 1
                    break
            
            # Add content to current chapter
            if current_chapter:
                current_chapter.content += text + "\n"
                current_chapter.estimated_words = len(current_chapter.content.split())
        
        # Don't forget last chapter
        if current_chapter:
            current_chapter.end_page = doc.page_count
            chapters.append(current_chapter)
        
        return chapters
    
    def _is_chapter_heading(self, text: str) -> bool:
        """
        Check if text matches chapter heading pattern
        """
        text = text.strip()
        if not text or len(text) > 100:  # Too long for a heading
            return False
        
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return True
        
        return False
    
    def _split_by_size(self, text: str, base_title: str) -> List[Chapter]:
        """
        Split text into chapters by size when no natural chapters found
        """
        words = text.split()
        chapters = []
        chunk_size = self.max_words_per_chapter
        
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chapters.append(Chapter(
                index=len(chapters),
                title=f"{base_title} - Part {len(chapters) + 1}",
                content=chunk_text,
                estimated_words=len(chunk_words)
            ))
        
        return chapters
    
    def _post_process_chapters(self, chapters: List[Chapter]) -> List[Chapter]:
        """
        Post-process chapters: split too long ones, merge too short ones
        """
        processed = []
        
        for chapter in chapters:
            # If chapter is too long, split it
            if chapter.estimated_words > self.max_words_per_chapter:
                sub_chapters = self._split_by_size(
                    chapter.content, 
                    chapter.title
                )
                for idx, sub in enumerate(sub_chapters):
                    sub.index = len(processed)
                    sub.title = f"{chapter.title} - Part {idx + 1}"
                    processed.append(sub)
            else:
                chapter.index = len(processed)
                processed.append(chapter)
        
        # Calculate estimated duration
        for chapter in processed:
            chapter.estimated_duration_seconds = (chapter.estimated_words / self.TTS_WPM) * 60
        
        return processed
    
    def _get_epub_content_by_href(self, book: epub.EpubBook, href: str, items: List) -> Optional[str]:
        """
        Get EPUB content by href reference
        """
        # Remove anchor if present
        if '#' in href:
            href = href.split('#')[0]
        
        for item in items:
            if item.get_name() == href or item.get_id() == href:
                content = item.get_content().decode('utf-8')
                soup = BeautifulSoup(content, 'html.parser')
                return soup.get_text()
        
        return None
    
    def _extract_all_epub_text(self, book: epub.EpubBook) -> str:
        """
        Extract all text from EPUB
        """
        all_text = ""
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            content = item.get_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            all_text += soup.get_text() + "\n"
        
        return all_text