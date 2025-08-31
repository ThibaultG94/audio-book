"""
Tests for Book Splitting Service
"""
import pytest
import tempfile
import json
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.services.splitter import BookSplitter, FileNamingService, TextCleaner
from app.services.detector import Chapter


class TestBookSplitter:
    """Test book splitting functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.splitter = BookSplitter(output_base_dir=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch.object(BookSplitter, '_extract_book_title')
    @patch('app.services.detector.ChapterDetector.detect_chapters')
    def test_split_book_success(self, mock_detect, mock_extract_title):
        """Test successful book splitting"""
        # Setup mocks
        mock_extract_title.return_value = "Test Book"
        mock_detect.return_value = [
            Chapter(
                index=0,
                title="Chapter 1",
                content="This is chapter 1 content.",
                estimated_words=5,
                estimated_duration_seconds=120
            ),
            Chapter(
                index=1,
                title="Chapter 2",
                content="This is chapter 2 content.",
                estimated_words=5,
                estimated_duration_seconds=120
            )
        ]
        
        # Create test file
        test_file = Path(self.temp_dir) / "test.pdf"
        test_file.write_text("Test content")
        
        # Split book
        result = self.splitter.split_book(
            file_path=str(test_file),
            file_type="pdf",
            book_title="Test Book",
            author="Test Author"
        )
        
        # Verify results
        assert result.book_title == "Test Book"
        assert result.total_chapters == 2
        assert len(result.chapters) == 2
        
        # Check manifest was created
        manifest_path = Path(result.manifest_path)
        assert manifest_path.exists()
        
        manifest = json.loads(manifest_path.read_text())
        assert manifest['book_title'] == "Test Book"
        assert manifest['author'] == "Test Author"
        assert manifest['total_chapters'] == 2
        assert manifest['file_type'] == "pdf"
        
        # Check chapter files were created
        for chapter_meta in result.chapters:
            chapter_file = Path(chapter_meta['text_file'])
            assert chapter_file.exists()
            content = chapter_file.read_text()
            assert len(content) > 0
            assert chapter_meta['status'] == 'pending'
            assert chapter_meta['word_count'] > 0
    
    def test_generate_book_id(self):
        """Test book ID generation"""
        # Create test file
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Test content")
        
        # Generate IDs
        id1 = self.splitter._generate_book_id(str(test_file))
        id2 = self.splitter._generate_book_id(str(test_file))
        
        # IDs should be different (timestamp component)
        assert id1 != id2
        
        # IDs should have expected format
        assert len(id1) == 12
        assert all(c in '0123456789abcdef' for c in id1)
    
    @patch('ebooklib.epub.read_epub')
    def test_extract_epub_title(self, mock_read_epub):
        """Test EPUB title extraction"""
        # Mock EPUB with metadata
        mock_book = MagicMock()
        mock_book.get_metadata.return_value = [["Great Book Title"]]
        mock_read_epub.return_value = mock_book
        
        title = self.splitter._extract_book_title("test.epub", "epub")
        assert title == "Great Book Title"
    
    @patch('fitz.open')
    def test_extract_pdf_title(self, mock_fitz_open):
        """Test PDF title extraction"""
        # Mock PDF with metadata
        mock_doc = MagicMock()
        mock_doc.metadata = {'title': 'PDF Book Title'}
        mock_fitz_open.return_value = mock_doc
        
        title = self.splitter._extract_book_title("test.pdf", "pdf")
        assert title == "PDF Book Title"
    
    def test_extract_title_fallback(self):
        """Test title extraction fallback to filename"""
        # Create test file
        test_file = Path(self.temp_dir) / "My_Great_Book.pdf"
        test_file.write_text("content")
        
        # Mock failed metadata extraction
        with patch('fitz.open', side_effect=Exception("Failed")):
            title = self.splitter._extract_book_title(str(test_file), "pdf")
        
        assert title == "My_Great_Book"
    
    def test_cleanup_book(self):
        """Test book cleanup"""
        # Create test book directory
        book_id = "test_book_123"
        book_dir = Path(self.temp_dir) / book_id
        book_dir.mkdir()
        
        # Add some files
        (book_dir / "manifest.json").write_text("{}")
        (book_dir / "chapter1.txt").write_text("content")
        
        # Cleanup
        success = self.splitter.cleanup_book(book_id)
        
        # Verify cleanup
        assert success
        assert not book_dir.exists()
        
        # Try cleanup non-existent book
        success = self.splitter.cleanup_book("non_existent")
        assert not success
    
    def test_get_split_info(self):
        """Test retrieving split info"""
        # Create test manifest
        book_id = "test_book_123"
        book_dir = Path(self.temp_dir) / book_id
        book_dir.mkdir()
        
        manifest = {
            "book_id": book_id,
            "book_title": "Test Book",
            "total_chapters": 2,
            "chapters": []
        }
        
        manifest_path = book_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest))
        
        # Get info
        info = self.splitter.get_split_info(book_id)
        
        # Verify
        assert info is not None
        assert info['book_id'] == book_id
        assert info['book_title'] == "Test Book"
        assert info['total_chapters'] == 2
        
        # Try non-existent book
        info = self.splitter.get_split_info("non_existent")
        assert info is None


class TestFileNamingService:
    """Test file naming functionality"""
    
    def setup_method(self):
        self.namer = FileNamingService()
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        # Test special character removal
        assert self.namer.sanitize_filename("Test: File/Name") == "Test_FileName"
        assert self.namer.sanitize_filename("Test <> Name") == "Test__Name"
        assert self.namer.sanitize_filename("Test|Name?") == "TestName"
        
        # Test whitespace handling
        assert self.namer.sanitize_filename("Test  Name") == "Test_Name"
        assert self.namer.sanitize_filename("  Test  ") == "Test"
        
        # Test length limiting
        long_name = "A" * 100
        sanitized = self.namer.sanitize_filename(long_name, max_length=50)
        assert len(sanitized) <= 50
        
        # Test edge cases
        assert self.namer.sanitize_filename("") == "untitled"
        assert self.namer.sanitize_filename("   ") == "untitled"
        assert self.namer.sanitize_filename("!!!") == "untitled"
    
    def test_generate_chapter_filename(self):
        """Test chapter filename generation"""
        filename = self.namer.generate_chapter_filename(
            book_title="Moby Dick",
            chapter_index=0,
            chapter_title="Chapter 1: Call Me Ishmael",
            author="Herman Melville"
        )
        
        # Verify format
        assert filename.startswith("000_")
        assert "Moby_Dick" in filename
        assert "Herman_Melville" in filename
        assert "Chapter_1" in filename
        
        # Test without author
        filename = self.namer.generate_chapter_filename(
            book_title="Test Book",
            chapter_index=10,
            chapter_title="Chapter 11"
        )
        
        assert filename.startswith("010_")
        assert "Test_Book" in filename
        assert "Chapter_11" in filename
        
        # Test with very long titles
        filename = self.namer.generate_chapter_filename(
            book_title="A" * 100,
            chapter_index=999,
            chapter_title="B" * 100,
            author="C" * 100
        )
        
        parts = filename.split("_")
        assert len(parts[0]) == 3  # Index
        assert len(parts[1]) <= 30  # Book title
        assert len(parts[2]) <= 20  # Author
        assert len(parts[3]) <= 30  # Chapter title
    
    def test_parse_chapter_filename(self):
        """Test parsing chapter filename"""
        # Test with author
        filename = "003_MobyDick_Melville_Chapter4.txt"
        parsed = self.namer.parse_chapter_filename(filename)
        
        assert parsed['index'] == 3
        assert parsed['book_title'] == "MobyDick"
        assert parsed['author'] == "Melville"
        assert parsed['chapter_title'] == "Chapter4"
        
        # Test without author
        filename = "010_TestBook_Chapter11.mp3"
        parsed = self.namer.parse_chapter_filename(filename)
        
        assert parsed['index'] == 10
        assert parsed['book_title'] == "TestBook"
        assert parsed['author'] is None
        assert parsed['chapter_title'] == "Chapter11"


class TestTextCleaner:
    """Test text cleaning functionality"""
    
    def setup_method(self):
        self.cleaner = TextCleaner()
    
    def test_clean_multiple_newlines(self):
        """Test multiple newline cleaning"""
        text = "Line 1\n\n\n\nLine 2\n\n\n\n\nLine 3"
        cleaned = self.cleaner.clean_for_tts(text)
        
        assert "\n\n\n" not in cleaned
        assert "\n\n" in cleaned  # Should preserve double newlines
    
    def test_clean_page_numbers(self):
        """Test page number removal"""
        text = "Text before\n42\nText after\nPage 5\nMore text"
        cleaned = self.cleaner.clean_for_tts(text)
        
        # Standalone numbers should be removed
        lines = cleaned.split('\n')
        assert "42" not in [line.strip() for line in lines]
        assert "Page 5" not in cleaned
        assert "Text before" in cleaned
        assert "Text after" in cleaned
    
    def test_fix_punctuation_spacing(self):
        """Test punctuation spacing fixes"""
        text = "Hello , world ! How are you ?"
        cleaned = self.cleaner.clean_for_tts(text)
        assert cleaned == "Hello, world! How are you?"
        
        text = "Test.No space"
        cleaned = self.cleaner.clean_for_tts(text)
        assert "Test.\nNo space" in cleaned or "Test. No space" in cleaned
    
    def test_normalize_quotes(self):
        """Test quote normalization"""
        # outer quotes are single; escape the inner single quote
        text = 'He said "Hello" and \'goodbye\''
        cleaned = self.cleaner.clean_for_tts(text)
        
        # Keep straight quotes
        assert '"Hello"' in cleaned
        assert "'goodbye'" in cleaned
        # Do not keep curly quotes
        assert "“" not in cleaned
        assert "”" not in cleaned
        assert "‘" not in cleaned
        assert "’" not in cleaned
    
    def test_remove_urls(self):
        """Test URL removal"""
        text = "Visit https://example.com for more. Also see http://test.org"
        cleaned = self.cleaner.clean_for_tts(text)
        
        assert "https://" not in cleaned
        assert "http://" not in cleaned
        assert "Visit" in cleaned
        assert "for more" in cleaned
    
    def test_clean_special_characters(self):
        """Test special character cleaning"""
        text = "Test™ with © symbols® and other§ stuff¶"
        cleaned = self.cleaner.clean_for_tts(text)
        
        # These special chars should be removed
        assert "™" not in cleaned
        assert "©" not in cleaned
        assert "®" not in cleaned
        assert "§" not in cleaned
        assert "¶" not in cleaned
        
        # Regular text should remain
        assert "Test" in cleaned
        assert "with" in cleaned
        assert "symbols" in cleaned
