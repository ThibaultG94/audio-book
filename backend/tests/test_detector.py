"""
Tests for Chapter Detection Service
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from app.services.detector import ChapterDetector, Chapter


class TestChapterDetector:
    """Test chapter detection functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.detector = ChapterDetector(max_chapter_duration_minutes=30)
    
    def test_is_chapter_heading(self):
        """Test chapter heading detection"""
        # Positive cases
        assert self.detector._is_chapter_heading("Chapter 1")
        assert self.detector._is_chapter_heading("CHAPTER 10: The Beginning")
        assert self.detector._is_chapter_heading("Part 3")
        assert self.detector._is_chapter_heading("Section 5")
        assert self.detector._is_chapter_heading("1. Introduction")
        assert self.detector._is_chapter_heading("IV. The Return")
        assert self.detector._is_chapter_heading("Chapitre 2")  # French
        
        # Negative cases
        assert not self.detector._is_chapter_heading("This is a regular paragraph")
        assert not self.detector._is_chapter_heading("")
        assert not self.detector._is_chapter_heading("A" * 150)  # Too long
        assert not self.detector._is_chapter_heading("   ")  # Whitespace only
    
    def test_split_by_size(self):
        """Test splitting text by size"""
        # Create large text
        text = " ".join(["word"] * 10000)  # 10000 words
        
        chapters = self.detector._split_by_size(text, "Test Book")
        
        # Check chapters were created
        assert len(chapters) > 1
        
        # Check each chapter respects max size
        for chapter in chapters:
            assert chapter.estimated_words <= self.detector.max_words_per_chapter
        
        # Check chapter naming
        assert chapters[0].title == "Test Book - Part 1"
        assert chapters[1].title == "Test Book - Part 2"
        
        # Check indexing
        for i, chapter in enumerate(chapters):
            assert chapter.index == i
    
    @patch('ebooklib.epub.read_epub')
    def test_detect_epub_chapters_with_toc(self, mock_read_epub):
        """Test EPUB chapter detection with TOC"""
        # Mock EPUB book with TOC
        mock_book = MagicMock()
        mock_toc_entry1 = MagicMock()
        mock_toc_entry1.title = "Chapter 1"
        mock_toc_entry1.href = "chapter1.xhtml"
        
        mock_toc_entry2 = MagicMock()
        mock_toc_entry2.title = "Chapter 2"
        mock_toc_entry2.href = "chapter2.xhtml"
        
        mock_book.toc = [mock_toc_entry1, mock_toc_entry2]
        
        # Mock content items
        mock_item1 = MagicMock()
        mock_item1.get_name.return_value = "chapter1.xhtml"
        mock_item1.get_content.return_value = b"<html><body>Chapter 1 content</body></html>"
        
        mock_item2 = MagicMock()
        mock_item2.get_name.return_value = "chapter2.xhtml"
        mock_item2.get_content.return_value = b"<html><body>Chapter 2 content</body></html>"
        
        mock_book.get_items_of_type.return_value = [mock_item1, mock_item2]
        mock_read_epub.return_value = mock_book
        
        # Test detection
        chapters = self.detector._detect_epub_chapters("test.epub")
        
        # Verify results
        assert len(chapters) == 2
        assert chapters[0].title == "Chapter 1"
        assert chapters[1].title == "Chapter 2"
        assert "Chapter 1 content" in chapters[0].content
        assert "Chapter 2 content" in chapters[1].content
    
    @patch('fitz.open')
    def test_detect_pdf_chapters_with_toc(self, mock_fitz_open):
        """Test PDF chapter detection with TOC"""
        # Mock PDF document
        mock_doc = MagicMock()
        mock_doc.page_count = 100
        mock_doc.metadata = {'title': 'Test PDF'}
        mock_doc.get_toc.return_value = [
            [1, "Chapter 1", 1],
            [1, "Chapter 2", 20],
            [1, "Chapter 3", 50],
            [2, "Subsection", 55]  # Should be ignored (level 2)
        ]
        
        # Mock pages
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Page content"
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.__iter__.return_value = [mock_page] * 100
        
        mock_fitz_open.return_value = mock_doc
        
        # Test detection
        chapters = self.detector._detect_pdf_chapters("test.pdf")
        
        # Verify results
        assert len(chapters) == 3  # Only level 1 TOC entries
        assert chapters[0].title == "Chapter 1"
        assert chapters[0].start_page == 1
        assert chapters[0].end_page == 19
        assert chapters[1].title == "Chapter 2"
        assert chapters[1].start_page == 20
        assert chapters[1].end_page == 49
    
    def test_post_process_chapters(self):
        """Test chapter post-processing"""
        # Create chapters with varying sizes
        chapters = [
            Chapter(
                index=0,
                title="Short Chapter",
                content="word " * 100,
                estimated_words=100
            ),
            Chapter(
                index=1,
                title="Long Chapter",
                content="word " * 10000,
                estimated_words=10000
            )
        ]
        
        processed = self.detector._post_process_chapters(chapters)
        
        # Short chapter should remain unchanged
        assert processed[0].title == "Short Chapter"
        
        # Long chapter should be split
        long_chapter_parts = [ch for ch in processed if "Long Chapter" in ch.title]
        assert len(long_chapter_parts) > 1
        
        # Check duration calculation
        for chapter in processed:
            assert chapter.estimated_duration_seconds > 0
            expected_duration = (chapter.estimated_words / self.detector.TTS_WPM) * 60
            assert abs(chapter.estimated_duration_seconds - expected_duration) < 1