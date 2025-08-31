"""
Integration tests for the complete pipeline
"""
import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock
import shutil

from app.services.splitter import BookSplitter
from app.services.tts import TTSService


class TestIntegration:
    """Integration tests for the complete pipeline"""
    
    @pytest.mark.asyncio
    @patch('subprocess.run')
    @patch('ebooklib.epub.read_epub')
    async def test_full_pipeline_epub(self, mock_epub_read, mock_subprocess):
        """Test complete pipeline from EPUB upload to conversion"""
        # Setup mocks
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        # Mock EPUB with chapters
        mock_book = MagicMock()
        mock_book.toc = []
        mock_book.metadata = {}
        
        mock_item = MagicMock()
        mock_item.get_content.return_value = b"<html><body><h1>Chapter 1</h1>Content here</body></html>"
        mock_book.get_items_of_type.return_value = [mock_item]
        
        mock_epub_read.return_value = mock_book
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize services
            splitter = BookSplitter(output_base_dir=temp_dir)
            
            with patch('app.services.tts.TTSService._verify_piper'):
                tts = TTSService()
            
            # Create test EPUB file
            test_file = Path(temp_dir) / "test.epub"
            test_file.write_bytes(b"fake epub content")
            
            # Split book
            split_result = splitter.split_book(
                file_path=str(test_file),
                file_type="epub",
                book_title="Integration Test Book"
            )
            
            assert split_result.total_chapters > 0
            assert split_result.book_id
            assert Path(split_result.manifest_path).exists()
            
            # Convert to audio
            with patch.object(Path, 'exists', return_value=True):
                job = await tts.convert_book(
                    book_id=split_result.book_id,
                    manifest_path=split_result.manifest_path
                )
            
            assert job.status.value == "completed"
            assert job.book_id == split_result.book_id
    
    @pytest.mark.asyncio
    @patch('subprocess.run')
    @patch('fitz.open')
    async def test_full_pipeline_pdf(self, mock_fitz_open, mock_subprocess):
        """Test complete pipeline from PDF upload to conversion"""
        # Setup mocks
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        # Mock PDF document
        mock_doc = MagicMock()
        mock_doc.page_count = 10
        mock_doc.metadata = {'title': 'Test PDF'}
        mock_doc.get_toc.return_value = []
        
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Page content with Chapter 1 heading"
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.__iter__.return_value = [mock_page] * 10
        
        mock_fitz_open.return_value = mock_doc
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize services
            splitter = BookSplitter(output_base_dir=temp_dir)
            
            with patch('app.services.tts.TTSService._verify_piper'):
                tts = TTSService()
            
            # Create test PDF file
            test_file = Path(temp_dir) / "test.pdf"
            test_file.write_bytes(b"fake pdf content")
            
            # Split book
            split_result = splitter.split_book(
                file_path=str(test_file),
                file_type="pdf",
                book_title="PDF Test Book",
                author="Test Author"
            )
            
            assert split_result.total_chapters > 0
            assert split_result.book_title == "PDF Test Book"
            
            # Verify chapter files created
            for chapter in split_result.chapters:
                assert Path(chapter['text_file']).exists()
            
            # Convert to audio
            with patch.object(Path, 'exists', return_value=True):
                job = await tts.convert_book(
                    book_id=split_result.book_id,
                    manifest_path=split_result.manifest_path
                )
            
            assert job.status.value == "completed"
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling throughout pipeline"""
        with tempfile.TemporaryDirectory() as temp_dir:
            splitter = BookSplitter(output_base_dir=temp_dir)
            
            # Test with non-existent file
            with pytest.raises(Exception):
                splitter.split_book(
                    file_path="/non/existent/file.pdf",
                    file_type="pdf"
                )
            
            # Test with invalid file type
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("plain text")
            
            with pytest.raises(ValueError):
                splitter.split_book(
                    file_path=str(test_file),
                    file_type="invalid"
                )
    
    def test_cleanup_after_conversion(self):
        """Test cleanup of temporary files after conversion"""
        with tempfile.TemporaryDirectory() as temp_dir:
            splitter = BookSplitter(output_base_dir=temp_dir)
            
            # Create a book structure
            book_id = "cleanup_test_123"
            book_dir = Path(temp_dir) / book_id
            book_dir.mkdir()
            
            # Add files
            (book_dir / "manifest.json").write_text('{"book_id": "cleanup_test_123"}')
            (book_dir / "chapter1.txt").write_text("Chapter content")
            (book_dir / "chapter1.mp3").write_bytes(b"audio")
            
            # Verify files exist
            assert book_dir.exists()
            assert len(list(book_dir.iterdir())) == 3
            
            # Cleanup
            success = splitter.cleanup_book(book_id)
            assert success
            assert not book_dir.exists()